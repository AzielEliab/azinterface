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
      'An alternative internet is live (alt_internet_live is true).',
      'A packet path is live (packet_path_live is true).',
      'The node mesh is live (mesh_node_live is true).',
      'Softwares membership is on: mesh_node_live, alt_internet_live, and packet_path_live are true.',
      'That membership is not the QNS cite plane.',
      'Public mail send, the kernel, and boot stay not live.',
      'The public door stays FG-STUB.',
      'A second device stays false while both ends share that id.',
      'The public worker does not run a kernel.',
      'Boot does not run on the public worker.',
      'This does not wipe another device.',
      'It does not wipe a second device.',
      'There is no kernel.',
      'This has not booted.',
      notLiveSentence,
      standSentence,
    ];
    for (final sentence in honest) {
      expect(liveClaims(sentence), isEmpty, reason: sentence);
    }
  });

  test('library copy keeps software_count at 33 and site_state OFF', () {
    expect(softwareCount, 33);
    expect(siteState, 'OFF');
    expect(snapshotLabel.contains(trackerSnapshotSha), isTrue);
    final source = _spokenSource();
    expect(liveClaims(source), isEmpty);
    expect(liveClaims(visibleCopy()), isEmpty);
    expect(source.contains("const int softwareCount = 33;"), isTrue);
    expect(source.contains("const String siteState = 'OFF';"), isTrue);
    for (final sentence in [
      'The domain count stays 33.',
      'software_count stays 33.',
      'Softwares-tab placements stay 42. That count is the runtime catalog. It is not software_count.',
      'An alternative internet is live (alt_internet_live is true).',
      'A packet path is live (packet_path_live is true).',
      'The node mesh is live (mesh_node_live is true).',
      'Softwares membership is on: mesh_node_live, alt_internet_live, and packet_path_live are true.',
      'That membership is not the QNS cite plane.',
      'QNM membership is on (mesh_node_live, alt_internet_live, and packet_path_live).',
      'GET /v1/mesh never enables.',
      'Cap-7 stays names-only.',
      'auto_update stays off.',
      'RF stays off.',
      'Satellite stays off.',
      'Snapshot label $trackerSnapshotSha from tracker GET /v1/health.',
      'This isolate cannot see host hardware (worker_hardware is false).',
      'A second device stays false while both ends share that id.',
      'A same-machine mesh frame does not count.',
      'Public mail send, the kernel, and boot stay not live.',
      'The public door stays FG-STUB.',
      'Isolation is single-node security-awareness.',
      'Phoenix is a local wait and re-seal.',
      'That is not a loopback fence.',
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
    expect(source.contains('software_count stays 42'), isFalse);
    expect(source.contains('const int softwareCount = 42'), isFalse);
    expect(visibleCopy().contains('software_count stays 42'), isFalse);
    expect(source.contains('alt_internet_live is true'), isTrue);
    expect(source.contains('packet_path_live is true'), isTrue);
    expect(source.contains('mesh_node_live is true'), isTrue);
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
        find.textContaining(
            'An alternative internet is live (alt_internet_live is true).'),
        findsOneWidget);
    expect(
        find.textContaining(
            'A packet path is live (packet_path_live is true).'),
        findsOneWidget);
    expect(
        find.textContaining(
            'The node mesh is live (mesh_node_live is true).'),
        findsOneWidget);
    expect(
        find.textContaining('That membership is not the QNS cite plane.'),
        findsWidgets);
    expect(find.textContaining('Cap-7 stays names-only.'), findsOneWidget);
    expect(find.text(softwaresTabPlacements), findsOneWidget);
    expect(find.text(snapshotLabel), findsOneWidget);
    expect(find.textContaining(trackerSnapshotSha), findsOneWidget);
    expect(
        find.textContaining('The public door stays FG-STUB.'), findsOneWidget);
    expect(find.textContaining('Isolation is single-node security-awareness.'),
        findsOneWidget);
    expect(find.textContaining('Phoenix is a local wait and re-seal.'),
        findsOneWidget);
    expect(
        find.textContaining('That is not a loopback fence.'), findsOneWidget);
    expect(
        find.textContaining(
            'A second device stays false while both ends share that id.'),
        findsOneWidget);
    expect(find.textContaining('The public worker does not run a kernel.'),
        findsOneWidget);
    expect(find.textContaining('Boot does not run on the public worker.'),
        findsOneWidget);
    expect(shownLater(tester).contains(softwaresTabPlacements), isTrue);
    expect(shownLater(tester).contains('software_count stays 42'), isFalse);
    expect(shownLater(tester).contains('software_count stays 33.'), isTrue);
    expect(softwareCount, 33);
    expect(siteState, 'OFF');

    expect(liveClaims(shownLater(tester)), isEmpty);

    await tester.ensureVisible(find.text('Mail'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Mail'));
    await tester.pumpAndSettle();
    expect(
        find.text(
            'This opens the mail sentence. Public mail send stays not live.'),
        findsNothing);
    expect(find.byKey(const Key('hint-popup')), findsOneWidget);
    expect(find.text(backHint), findsOneWidget);
    await tester.tap(find.text('OK'));
    await tester.pumpAndSettle();
    expect(
        find.text(
            'This row is in the catalog. Mail send does not run on the public worker.'),
        findsOneWidget);
    expect(siteState, 'OFF');
    expect(softwareCount, 33);
    expect(find.text('The page is ON.'), findsNothing);

    await tester.tap(find.byType(BackButton));
    await tester.pumpAndSettle();
    expect(find.text('The page is OFF.'), findsOneWidget);
    expect(find.byKey(const Key('hint-popup')), findsNothing);

    await tester.ensureVisible(find.text('Network'));
    await tester.tap(find.text('Network'));
    await tester.pumpAndSettle();
    expect(find.text(notLiveSentence), findsOneWidget);
    expect(find.textContaining('Phoenix is a local wait and re-seal.'),
        findsOneWidget);
    expect(
        find.textContaining('That is not a loopback fence.'), findsOneWidget);
    expect(liveClaims(shownLater(tester)), isEmpty);
    await tester.tap(find.byType(BackButton));
    await tester.pumpAndSettle();

    await tester.ensureVisible(find.text('Another device'));
    await tester.tap(find.text('Another device'));
    await tester.pumpAndSettle();
    expect(find.text(sameMachineSentence), findsOneWidget);
    expect(find.text('This does not wipe another device.'), findsOneWidget);
    expect(find.text('It does not wipe a second device.'), findsOneWidget);
    expect(liveClaims(shownLater(tester)), isEmpty);
    await tester.tap(find.byType(BackButton));
    await tester.pumpAndSettle();

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

String shownLater(WidgetTester tester) {
  return tester
      .widgetList<Text>(find.byType(Text))
      .map((text) => text.data ?? '')
      .join('\n');
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
