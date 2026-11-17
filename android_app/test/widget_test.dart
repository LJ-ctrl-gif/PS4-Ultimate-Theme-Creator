import 'package:flutter_test/flutter_test.dart';
import 'package:ps4_theme_builder/main.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('renders the theme builder dashboard', (tester) async {
    await tester.pumpWidget(const ThemeBuilderApp());
    await tester.pump();
    expect(find.text('PS4 THEME BUILDER'), findsOneWidget);
    expect(find.text('YOUR THEME PROJECT'), findsOneWidget);
  });
}
