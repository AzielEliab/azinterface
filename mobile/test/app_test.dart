import 'dart:io';

import 'package:azinterface/claims.dart';
import 'package:azinterface/facts.dart';
import 'package:azinterface/hints.dart';
import 'package:azinterface/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  test('checker flags each refused door when a sentence calls it live', () {
    const samples = {
      'public mail send': 'Public mail send is live.',
      'packet path': 'The packet path is live.',
      'alternative internet': 'An alternative internet is live.',
      'kernel': 'The kernel is live.',
      'boot': 'Boot is live.',
      'second device': 'A second device is live.',
    };
    samples.forEach((name, sentence) {
      expect(liveClaims(sentence), contains(name), reason: sentence);
    });
    expect(liveClaims('The public worker runs a kernel.'), contains('kernel'));
    expect(liveClaims('Boot has booted.'), contains('boot'));
    expect(
        liveClaims('This wipes a second device.'), contains('second device'));
    expect(liveClaims('This wipes another device.'), contains('second device'));

    const honest = [
      'Mail send does not run on the public worker.',
      'The packet path does not run.',
      'An alternative internet does not run.',
      'The public worker does not run a kernel.',
      'Boot does not run on the public worker.',
      'This does not wipe another device.',
      'It does not wipe a second device.',
      'There is no kernel.',
      'This has not booted.',
      standSentence,
    ];
    for (final sentence in honest) {
      expect(liveClaims(sentence), isEmpty, reason: sentence);
    }
  });

  test('library copy keeps software_count at 33 and site_state OFF', () {
    expect(softwareCount, 33);
    expect(siteState, 'OFF');
    final source = _spokenSource();
    expect(liveClaims(source), isEmpty);
    expect(liveClaims(visibleCopy()), isEmpty);
    expect(source.contains("const int softwareCount = 33;"), isTrue);
    expect(source.contains("const String siteState = 'OFF';"), isTrue);
    for (final sentence in [
      'The domain count stays 33.',
      'Softwares 42 is the runtime catalog.',
      'The packet path does not run.',
      'An alternative internet does not run.',
      'WARN-5 stands.',
      'Mail send does not run on the public worker.',
      'The public worker does not run a kernel.',
      'Boot does not run on the public worker.',
      'The host operating system stays the host operating system.',
      'AZNews can stand alone.',
      '4DMap can stand alone.',
      'This does not wipe another device.',
      'It does not wipe a second device.',
      'There is no kernel.',
      'This has not booted.',
    ]) {
      expect(source.contains(sentence), isTrue, reason: sentence);
    }
    expect(source.contains('Internet is not live.'), isFalse);
    expect(source.toLowerCase().contains('installed'), isFalse);
    expect(source.contains('One-click'), isFalse);
    expect(source.contains('Play Store'), isFalse);
    expect(source.contains('App Store'), isFalse);
  });

  testWidgets('a new user gets one hint per control and the page stays OFF',
      (tester) async {
    SharedPreferences.setMockInitialValues({});
    final prefs = await SharedPreferences.getInstance();
    await tester.pumpWidget(AzInterfaceApp(book: HintBook(prefs)));
    await dismissHints(tester, sentenceControls.length);

    expect(find.byKey(const Key('hint-popup')), findsNothing);
    expect(find.text('The page is OFF.'), findsOneWidget);
    expect(find.text('The domain count stays 33.'), findsWidgets);
    expect(find.textContaining('Mail send does not run on the public worker.'),
        findsOneWidget);
    expect(
        find.textContaining('The packet path does not run.'), findsOneWidget);
    expect(find.textContaining('An alternative internet does not run.'),
        findsOneWidget);
    expect(find.textContaining('The public worker does not run a kernel.'),
        findsOneWidget);
    expect(find.textContaining('Boot does not run on the public worker.'),
        findsOneWidget);
    expect(softwareCount, 33);
    expect(siteState, 'OFF');

    final shown = tester
        .widgetList<Text>(find.byType(Text))
        .map((text) => text.data ?? '')
        .join('\n');
    expect(liveClaims(shown), isEmpty);

    await tester.tap(find.text('Mail'));
    await tester.pumpAndSettle();
    expect(
        find.text(
            'This opens the mail sentence. Public mail send does not run on the public worker.'),
        findsNothing);
    expect(find.byKey(const Key('hint-popup')), findsOneWidget);
    expect(find.text(backHint), findsOneWidget);
    await tester.tap(find.text('OK'));
    await tester.pumpAndSettle();
    expect(
        find.text(
            'This row is in the catalog. Mail send does not run on the public worker.'),
        findsOneWidget);
    expect(
        tester.widget<Text>(find.byKey(const Key('site-state-sentence'))).data,
        'The page is OFF.');
    expect(find.text('The page is ON.'), findsNothing);

    await tester.tap(find.byType(BackButton));
    await tester.pumpAndSettle();
    expect(find.text('The page is OFF.'), findsOneWidget);
    expect(find.byKey(const Key('hint-popup')), findsNothing);

    await tester.pumpWidget(const SizedBox.shrink());
    await tester.pumpWidget(AzInterfaceApp(book: HintBook(prefs)));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.byKey(const Key('hint-popup')), findsNothing);
    expect(find.text('The page is OFF.'), findsOneWidget);
  });
}

Future<void> dismissHints(WidgetTester tester, int count) async {
  for (var i = 0; i < count; i++) {
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));
    expect(find.byKey(const Key('hint-popup')), findsOneWidget);
    await tester.tap(find.text('OK'));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 400));
  }
  await tester.pump(const Duration(milliseconds: 400));
  expect(find.byKey(const Key('hint-popup')), findsNothing);
}

String _spokenSource() {
  final buffer = StringBuffer();
  for (final entity in Directory('lib').listSync(recursive: true)) {
    if (entity is File &&
        entity.path.endsWith('.dart') &&
        !entity.path.endsWith('claims.dart')) {
      buffer.writeln(entity.readAsStringSync());
    }
  }
  return buffer.toString();
}
