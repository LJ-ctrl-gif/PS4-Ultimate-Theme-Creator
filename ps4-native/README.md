# VOID THEME BUILDER — Native PS4 Application

## Product target

A standalone PS4 homebrew application launched from the PS4 home screen. This is a separate native frontend target; the existing browser/Termux editor remains a development and media-processing companion, not the final PS4 application.

Target hardware: PS4 Slim (CUH-2216B), with GoldHEN on firmware 13.52.

## Main navigation

- Home — recent projects, create theme, open project, build status.
- PS4 Files — browse only filesystem locations readable by the running homebrew process; preview and select local assets.
- Wallpaper Studio — still-image selection (PNG/JPG), crop/fit controls, preview.
- Dynamic Studio — MP4 import, preview, start/end trim, loop toggle, saved clip presets. MP4 is an import source; export must convert to the PS4 theme RAF scene format and enforce the verified frame-count and size limits.
- Sound Studio — MP3 and other supported audio import, preview, trim/loop where supported, convert to ATRAC9 .at9 for home music and VAG for effects.
- Function & Logo Studio — choose supported function-icon slots, select/import PNG assets, preview normal and glow variants, restore defaults. The app's own logo and theme preview branding are separate from system function icons.
- Theme Library — save, duplicate, rename, reopen, and delete project manifests and generated assets.
- Preview — render home, top-menu, and apply-theme mockups before export.
- Package Builder — validate assets and metadata, then invoke an authorized compatible PS4 theme packaging toolchain when present.
- Settings — storage location, media cache, controller hints, diagnostics, and reset.

## Controller behavior

- D-pad / left stick: move focus.
- Cross: select / confirm.
- Circle: back / cancel.
- L1/R1: switch major tabs where appropriate.
- L2/R2: scrub timeline or adjust values where appropriate.
- Options: context actions.
- Every screen must show focus state and controller hints; keyboard/mouse must not be required.

## File browser and media safety

- Show the current path, breadcrumbs, file type, size, and readable status.
- Allow re-opening the browser for every asset slot; changing one slot must not lock the user into a previous folder.
- Support internal storage and attached USB paths only when the OS/homebrew permissions expose them.
- Do not claim unrestricted access to protected system or other applications' private data.
- Filter by file extension but validate actual file contents before decoding.
- Handle unreadable, corrupt, oversized, or unsupported files with a visible error and no crash.
- Copy selected source files into the project's own workspace before processing; never overwrite originals.

## Theme format and validation

The existing theme generator defines the current known output layout:

```
Image0/
  theme.xml
  texture/background/
  texture/function_icon/
  texture/content_icon/
  scene/background.raf/   # optional dynamic scene
  sound/bgm_home.at9      # optional
  sound/se_decide.vag
  sound/se_cursor.vag
  sound/se_cancel.vag
Sc0/
  param.sfo
  icon0.png
  pic1.png
```

Keep the existing verified constraints in `app/config.py` and the theme-format tests as the source of truth. In particular, animated RAF output has strict frame-count and total-size limits. MP4 is not copied into the final theme package as a playable video.

Function icon replacement is limited to supported theme slots. A theme cannot arbitrarily replace every PS4 system icon, rename every system function, or change system behavior. The UI must label unsupported requests clearly and never generate misleading packages.

## Proposed native architecture

- Native UI and controller loop: C/C++ application built with a compatible PS4 homebrew SDK/toolchain.
- Project model: versioned JSON manifest plus copied asset files.
- File browser: platform filesystem APIs with explicit readable-path checks.
- Media conversion: reuse the existing tested conversion/asset pipeline where it can be ported; otherwise run conversion in a separate supported build environment and import validated outputs.
- Theme assembly: reuse the existing theme layout, XML, RAF, VAG, ATRAC9 and package validation modules where practical.
- Packaging: require a user-provided, authorized compatible packaging toolchain. Do not bundle or redistribute proprietary Sony executables.
- Diagnostics: log each import, conversion, validation and packaging stage; preserve logs when a build fails.

## Suggested project layout

```
ps4-native/
  README.md
  CMakeLists.txt
  src/
    main.cpp
    app.cpp
    controller.cpp
    navigation.cpp
    file_browser.cpp
    project_store.cpp
    media_import.cpp
    theme_export.cpp
    screens/
      home.cpp
      wallpaper.cpp
      dynamic.cpp
      sounds.cpp
      functions.cpp
      library.cpp
      preview.cpp
      package.cpp
  assets/
    icons/
    fonts/
  tests/
    project_manifest_tests.cpp
```

## Build gates

1. Confirm a compatible PS4 homebrew SDK and target runtime are available.
2. Build and launch a minimal native app with controller input and a black/red UI.
3. Add a safe directory browser and project save/load.
4. Add image and audio import with validation.
5. Integrate the already-tested theme conversion and assembly logic.
6. Add dynamic RAF conversion and enforce format limits.
7. Add function icon slot editing and full preview.
8. Integrate authorized package tooling and validate the resulting PKG on a test setup.

## Current status

This document records the native-app target and implementation requirements. It is not a compiled PS4 application or installable PKG. The existing repository is currently a local web application with Android/Termux artwork editing; a native PS4 executable still requires the compatible PS4 SDK/toolchain and runtime implementation.
