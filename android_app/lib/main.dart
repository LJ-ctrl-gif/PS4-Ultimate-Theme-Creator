import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';

import 'package:archive/archive.dart';
import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:just_audio/just_audio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() => runApp(const ThemeBuilderApp());

const blue = Color(0xFF38A9FF);
const bg = Color(0xFF080B10);
const panel = Color(0xFF121923);
const panel2 = Color(0xFF1A2634);

class ThemeBuilderApp extends StatelessWidget {
  const ThemeBuilderApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        title: 'PS4 Theme Builder',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          brightness: Brightness.dark,
          scaffoldBackgroundColor: bg,
          colorScheme: ColorScheme.fromSeed(
            seedColor: blue,
            brightness: Brightness.dark,
            surface: panel,
          ),
          appBarTheme: const AppBarTheme(
            backgroundColor: bg,
            foregroundColor: Colors.white,
            elevation: 0,
          ),
          cardTheme: CardThemeData(
            color: panel,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(18),
            ),
          ),
          inputDecorationTheme: InputDecorationTheme(
            filled: true,
            fillColor: panel2,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: BorderSide.none,
            ),
          ),
        ),
        home: const BuilderHome(),
      );
}

class BuilderHome extends StatefulWidget {
  const BuilderHome({super.key});

  @override
  State<BuilderHome> createState() => _BuilderHomeState();
}

class _BuilderHomeState extends State<BuilderHome> {
  final _tabs = const [
    NavigationDestination(icon: Icon(Icons.home_outlined), label: 'Home'),
    NavigationDestination(icon: Icon(Icons.wallpaper_outlined), label: 'Editor'),
    NavigationDestination(icon: Icon(Icons.music_note_outlined), label: 'Audio'),
    NavigationDestination(icon: Icon(Icons.ios_share_outlined), label: 'Export'),
  ];
  final _audio = AudioPlayer();
  final Map<String, String> _assets = {};
  final Map<String, Uint8List> _imageData = {};
  final _nameController = TextEditingController(text: 'Midnight Graphite');
  int _tab = 0;
  bool _busy = false;
  String? _playing;

  static const imageSlots = <String, String>{
    'Home background': 'Main PS4 home-screen wallpaper',
    'Top menu background': 'Background for the PS4 function area',
    'Theme thumbnail': 'Preview image shown in the theme picker',
    'Home icon': 'Theme home/content icon artwork',
    'Library icon': 'Library function icon artwork',
    'Settings icon': 'Settings function icon artwork',
  };
  static const audioSlots = <String, String>{
    'Background / Menu': 'Menu music',
    'Navigation': 'Move between menu items',
    'Confirm': 'Confirm a selection',
    'Exit / Cancel': 'Return or cancel',
  };

  @override
  void initState() {
    super.initState();
    _loadProject();
  }

  Future<Directory> _assetDirectory() async {
    final root = await getApplicationDocumentsDirectory();
    final dir = Directory('${root.path}/theme_assets');
    if (!await dir.exists()) await dir.create(recursive: true);
    return dir;
  }

  Future<void> _loadProject() async {
    final prefs = await SharedPreferences.getInstance();
    final saved = prefs.getString('theme_assets');
    if (saved != null) {
      final decoded = jsonDecode(saved) as Map<String, dynamic>;
      for (final entry in decoded.entries) {
        final file = File(entry.value as String);
        if (await file.exists()) _assets[entry.key] = file.path;
      }
    }
    if (mounted) setState(() {});
  }

  Future<void> _persist() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('theme_assets', jsonEncode(_assets));
    await prefs.setString('theme_name', _nameController.text.trim());
  }

  void _notice(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }

  Future<void> _pickAsset(String slot, {required bool audio}) async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: audio ? FileType.audio : FileType.image,
        withData: true,
      );
      if (result == null || result.files.isEmpty) return;
      final picked = result.files.single;
      final bytes = picked.bytes;
      if (bytes == null) {
        _notice('Could not read this file. Please choose it again.');
        return;
      }
      final dir = await _assetDirectory();
      final safeName = picked.name.replaceAll(RegExp(r'[^A-Za-z0-9._-]'), '_');
      final target = File('${dir.path}/${DateTime.now().microsecondsSinceEpoch}_$safeName');
      await target.writeAsBytes(bytes, flush: true);
      setState(() {
        _assets[slot] = target.path;
        if (!audio) _imageData[slot] = Uint8List.fromList(bytes);
      });
      await _persist();
      _notice('${picked.name} added to $slot');
    } catch (error) {
      _notice('Could not add file: $error');
    }
  }

  Future<void> _toggleAudio(String slot) async {
    final path = _assets[slot];
    if (path == null) return;
    try {
      if (_playing == slot) {
        await _audio.stop();
        setState(() => _playing = null);
      } else {
        await _audio.setFilePath(path);
        await _audio.play();
        setState(() => _playing = slot);
        _audio.playerStateStream.listen((state) {
          if (state.processingState == ProcessingState.completed && mounted) {
            setState(() => _playing = null);
          }
        });
      }
    } catch (error) {
      _notice('Audio preview failed: $error');
    }
  }

  Future<void> _removeAsset(String slot) async {
    final path = _assets.remove(slot);
    _imageData.remove(slot);
    if (path != null) {
      final file = File(path);
      if (await file.exists()) await file.delete();
    }
    await _persist();
    if (mounted) setState(() {});
  }

  Future<void> _exportProject() async {
    setState(() => _busy = true);
    try {
      await _persist();
      final archive = Archive();
      final manifest = <String, dynamic>{
        'format': 'ps4-theme-builder-project',
        'schemaVersion': 1,
        'themeName': _nameController.text.trim(),
        'createdAt': DateTime.now().toUtc().toIso8601String(),
        'assets': <String, String>{},
        'notice': 'Editable project archive; not an installable PS4 PKG.',
      };
      for (final entry in _assets.entries) {
        final file = File(entry.value);
        if (!await file.exists()) continue;
        final bytes = await file.readAsBytes();
        final name = 'assets/${entry.key.replaceAll(RegExp(r'[^A-Za-z0-9_-]'), '_')}_${file.uri.pathSegments.last.split('.').last}';
        archive.addFile(ArchiveFile(name, bytes.length, bytes));
        (manifest['assets'] as Map<String, String>)[entry.key] = name;
      }
      final jsonBytes = utf8.encode(const JsonEncoder.withIndent('  ').convert(manifest));
      archive.addFile(ArchiveFile('project.json', jsonBytes.length, jsonBytes));
      final zipped = ZipEncoder().encode(archive);
      if (zipped == null) throw StateError('ZIP export returned no data.');
      final root = await getApplicationDocumentsDirectory();
      final out = File('${root.path}/${_safeProjectName()}_project.zip');
      await out.writeAsBytes(zipped, flush: true);
      await SharePlus.instance.share(ShareParams(
        title: 'Export ${_nameController.text}',
        text: 'Editable PS4 Theme Builder project archive. This is not a PS4 PKG.',
        files: [XFile(out.path)],
      ));
      _notice('Project archive created.');
    } catch (error) {
      _notice('Export failed: $error');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  String _safeProjectName() {
    final value = _nameController.text.trim().replaceAll(RegExp(r'[^A-Za-z0-9_-]'), '_');
    return value.isEmpty ? 'my_theme' : value;
  }

  int get _imageCount => imageSlots.keys.where(_assets.containsKey).length;
  int get _audioCount => audioSlots.keys.where(_assets.containsKey).length;

  @override
  void dispose() {
    _audio.dispose();
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        appBar: AppBar(
          title: const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('PS4 THEME BUILDER', style: TextStyle(fontSize: 11, color: blue, letterSpacing: 1.4, fontWeight: FontWeight.bold)),
              SizedBox(height: 3),
              Text('Midnight workspace', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
            ],
          ),
          actions: [
            Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(color: panel2, borderRadius: BorderRadius.circular(20)),
                  child: const Text('ANDROID BETA', style: TextStyle(color: blue, fontSize: 9, fontWeight: FontWeight.bold)),
                ),
              ),
            ),
          ],
        ),
        body: SafeArea(
          child: IndexedStack(
            index: _tab,
            children: [
              _dashboard(),
              _assetEditor(),
              _audioEditor(),
              _exportPage(),
            ],
          ),
        ),
        bottomNavigationBar: NavigationBar(
          selectedIndex: _tab,
          destinations: _tabs,
          onDestinationSelected: (index) => setState(() => _tab = index),
        ),
      );

  Widget _dashboard() => ListView(
        padding: const EdgeInsets.all(18),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(22),
              gradient: const LinearGradient(colors: [Color(0xFF17283B), Color(0xFF101722)]),
              border: Border.all(color: blue.withValues(alpha: .25)),
            ),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('YOUR THEME PROJECT', style: TextStyle(color: blue, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.3)),
              const SizedBox(height: 12),
              Text(_nameController.text, style: const TextStyle(fontSize: 25, fontWeight: FontWeight.w800)),
              const SizedBox(height: 8),
              const Text('Personalize backgrounds, icons and menu sounds.', style: TextStyle(color: Colors.white70)),
              const SizedBox(height: 18),
              TextField(controller: _nameController, decoration: const InputDecoration(labelText: 'Project name', prefixIcon: Icon(Icons.edit_outlined)), onChanged: (_) => setState(() {}), onSubmitted: (_) => _persist()),
            ]),
          ),
          const SizedBox(height: 22),
          const Text('PROJECT OVERVIEW', style: TextStyle(color: Colors.white60, fontSize: 11, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
          const SizedBox(height: 10),
          Row(children: [
            Expanded(child: _statCard('Images', '$_imageCount / ${imageSlots.length}', Icons.image_outlined)),
            const SizedBox(width: 10),
            Expanded(child: _statCard('Audio', '$_audioCount / ${audioSlots.length}', Icons.music_note)),
          ]),
          const SizedBox(height: 10),
          _statCard('Project status', 'Editable project • not packaged', Icons.folder_open, wide: true),
          const SizedBox(height: 18),
          _actionCard('Customize backgrounds & icons', 'Choose images from your device', Icons.wallpaper, () => setState(() => _tab = 1)),
          _actionCard('Assign menu sounds', 'Add music and sound effects', Icons.graphic_eq, () => setState(() => _tab = 2)),
          _actionCard('Export project archive', 'Save and share your editable project', Icons.ios_share, () => setState(() => _tab = 3)),
        ],
      );

  Widget _statCard(String title, String value, IconData icon, {bool wide = false}) => Container(
        width: wide ? double.infinity : null,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(16)),
        child: Row(children: [
          Icon(icon, color: blue),
          const SizedBox(width: 12),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(title, style: const TextStyle(fontSize: 12, color: Colors.white60)),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700)),
          ])),
        ]),
      );

  Widget _actionCard(String title, String subtitle, IconData icon, VoidCallback onTap) => Card(
        margin: const EdgeInsets.only(bottom: 9),
        child: ListTile(
          onTap: onTap,
          leading: Icon(icon, color: blue),
          title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
          subtitle: Text(subtitle, style: const TextStyle(fontSize: 11, color: Colors.white60)),
          trailing: const Icon(Icons.chevron_right, color: blue),
        ),
      );

  Widget _assetEditor() => ListView(
        padding: const EdgeInsets.all(18),
        children: [
          _sectionTitle('Theme editor', 'Choose the images used by your theme.'),
          const SizedBox(height: 16),
          ...imageSlots.entries.map((entry) => _assetTile(entry.key, entry.value, audio: false)),
          const SizedBox(height: 12),
          const Text('Use images you own or are authorized to use. Image conversion and PS4 compatibility checks are handled by the desktop builder for now.', style: TextStyle(color: Colors.white54, fontSize: 11, height: 1.5)),
        ],
      );

  Widget _audioEditor() => ListView(
        padding: const EdgeInsets.all(18),
        children: [
          _sectionTitle('Audio setup', 'Assign your own music and sound files.'),
          const SizedBox(height: 16),
          ...audioSlots.entries.map((entry) => _assetTile(entry.key, entry.value, audio: true)),
          const SizedBox(height: 12),
          const Text('Audio preview plays the selected source file. PS4-specific ATRAC9 / VAG conversion is not performed by this Android beta.', style: TextStyle(color: Colors.white54, fontSize: 11, height: 1.5)),
        ],
      );

  Widget _sectionTitle(String title, String subtitle) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontSize: 25, fontWeight: FontWeight.w800)),
        const SizedBox(height: 5),
        Text(subtitle, style: const TextStyle(color: Colors.white60, fontSize: 12)),
      ]);

  Widget _assetTile(String slot, String description, {required bool audio}) {
    final path = _assets[slot];
    final present = path != null;
    final isPlaying = _playing == slot;
    final fileName = present ? path.split('/').last : 'No file selected';
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(16)),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Icon(audio ? Icons.music_note : Icons.image_outlined, color: blue),
          const SizedBox(width: 10),
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(slot, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
            Text(description, style: const TextStyle(color: Colors.white54, fontSize: 10)),
          ])),
          if (present && audio)
            IconButton(onPressed: () => _toggleAudio(slot), icon: Icon(isPlaying ? Icons.stop_circle_outlined : Icons.play_circle_outline, color: blue)),
          if (present)
            IconButton(onPressed: () => _removeAsset(slot), icon: const Icon(Icons.close, color: Colors.white54)),
        ]),
        if (present && !audio && _imageData[slot] != null)
          Padding(
            padding: const EdgeInsets.only(top: 10, bottom: 8),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: Image.memory(_imageData[slot]!, height: 125, width: double.infinity, fit: BoxFit.cover),
            ),
          ),
        const SizedBox(height: 7),
        Text(fileName, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(color: Colors.white60, fontSize: 10)),
        const SizedBox(height: 10),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: () => _pickAsset(slot, audio: audio),
            icon: Icon(present ? Icons.swap_horiz : Icons.add, size: 17),
            label: Text(present ? 'Replace file' : audio ? 'Choose audio file' : 'Choose image'),
          ),
        ),
      ]),
    );
  }

  Widget _exportPage() => ListView(
        padding: const EdgeInsets.all(18),
        children: [
          _sectionTitle('Preview & export', 'Review your project and save an editable archive.'),
          const SizedBox(height: 18),
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(color: panel, borderRadius: BorderRadius.circular(18)),
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Text('PROJECT SUMMARY', style: TextStyle(color: blue, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1.2)),
              const SizedBox(height: 10),
              Text(_nameController.text, style: const TextStyle(fontSize: 21, fontWeight: FontWeight.w800)),
              const SizedBox(height: 12),
              _summaryRow('Image assets', '$_imageCount / ${imageSlots.length}'),
              _summaryRow('Audio assets', '$_audioCount / ${audioSlots.length}'),
              _summaryRow('Project archive', 'Ready to export'),
            ]),
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: const Color(0xFF302817), borderRadius: BorderRadius.circular(14), border: Border.all(color: const Color(0xFF80612A))),
            child: const Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Icon(Icons.info_outline, color: Color(0xFFFFC66D)),
              SizedBox(width: 10),
              Expanded(child: Text('This beta exports an editable ZIP project only. It does not create an installable PS4 PKG. PS4 packaging requires the compatible authorized toolchain and a separate tested build environment.', style: TextStyle(color: Color(0xFFFFDCA0), fontSize: 11, height: 1.5))),
            ]),
          ),
          const SizedBox(height: 18),
          FilledButton.icon(
            onPressed: _busy ? null : _exportProject,
            icon: _busy ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.archive_outlined),
            label: Text(_busy ? 'Preparing archive…' : 'Export editable project ZIP'),
            style: FilledButton.styleFrom(backgroundColor: blue, foregroundColor: Colors.black, minimumSize: const Size.fromHeight(52)),
          ),
        ],
      );

  Widget _summaryRow(String label, String value) => Padding(
        padding: const EdgeInsets.only(top: 10),
        child: Row(children: [
          Expanded(child: Text(label, style: const TextStyle(color: Colors.white60, fontSize: 12))),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 12)),
        ]),
      );
}
