// Sentences a person reads. Same facts as the public worker, aziel-runtime,
// and AZ-OS. software_count stays 33. site_state stays OFF.

const int softwareCount = 33;
const String siteState = 'OFF';

const String standSentence =
    'This page stands on its own. Calls to aziel-runtime still use the existing FragGate door. '
    'Softwares 42 is the runtime catalog. The domain count stays 33. '
    'The packet path does not run. An alternative internet does not run. WARN-5 stands. '
    'Mail send does not run on the public worker. The public worker does not run a kernel. '
    'Boot does not run on the public worker. The host operating system stays the host operating system. '
    'AZNews can stand alone. 4DMap can stand alone. A story is a pin only after that story is read back.';

const String backHint = 'This returns to the sentence list.';

class SentenceControl {
  const SentenceControl({
    required this.id,
    required this.label,
    required this.hint,
    required this.title,
    required this.sentences,
  });

  final String id;
  final String label;
  final String hint;
  final String title;
  final List<String> sentences;
}

const List<SentenceControl> sentenceControls = [
  SentenceControl(
    id: 'site-state',
    label: 'Site state',
    hint: 'This opens the site-state sentence. The page is OFF.',
    title: 'Site state',
    sentences: [
      'The page is OFF.',
      'Living presence is off.',
      'Sealed cycle: OFF → integrity → ON → FULL SHUTDOWN → MEMORIAL. One step only. No skip.',
      'There is no cloud-asleep mode.',
    ],
  ),
  SentenceControl(
    id: 'domain-count',
    label: 'Domain count',
    hint: 'This opens the domain count. It stays 33.',
    title: 'Domain count',
    sentences: [
      'The domain count stays 33.',
      'Softwares 42 is the runtime catalog.',
      'That list is the runtime catalog. It is not the domain count.',
    ],
  ),
  SentenceControl(
    id: 'mail',
    label: 'Mail',
    hint:
        'This opens the mail sentence. Public mail send does not run on the public worker.',
    title: 'Mail',
    sentences: [
      'This row is in the catalog. Mail send does not run on the public worker.',
    ],
  ),
  SentenceControl(
    id: 'network',
    label: 'Network',
    hint: 'This opens the network sentence. The packet path does not run.',
    title: 'Network',
    sentences: [
      'This row is in the catalog. The packet path does not run. An alternative internet does not run. WARN-5 stands.',
    ],
  ),
  SentenceControl(
    id: 'azos',
    label: 'AZ-OS',
    hint:
        'This opens the AZ-OS sentence. The public worker does not run a kernel.',
    title: 'AZ-OS',
    sentences: [
      'This row is in the catalog. The public worker does not run a kernel. Boot does not run on the public worker.',
      'The host operating system stays the host operating system.',
      'There is no kernel.',
      'This has not booted.',
    ],
  ),
  SentenceControl(
    id: 'second-device',
    label: 'Another device',
    hint:
        'This opens the Scorched Earth sentence. It does not wipe a second device.',
    title: 'Scorched Earth',
    sentences: [
      'Scorched Earth is a local advisory.',
      'This does not wipe another device.',
      'It does not wipe a second device.',
    ],
  ),
];

String visibleCopy() {
  final parts = <String>[
    'AZInterface',
    'Aziel Eliab',
    'Interface is CUSTODY.',
    standSentence,
    'The page is $siteState.',
    'The domain count stays $softwareCount.',
    backHint,
    'What this control does',
    for (final control in sentenceControls) ...[
      control.label,
      control.hint,
      control.title,
      ...control.sentences,
    ],
  ];
  return parts.join('\n');
}
