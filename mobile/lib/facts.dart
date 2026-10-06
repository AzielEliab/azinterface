// Sentences a person reads. Same not-live contract as the public worker.
// software_count stays 33. site_state stays OFF. Live flags stay false.

const int softwareCount = 33;
const String siteState = 'OFF';

// Isolate form of the worker sentence. This app does not invent a machine id.
const String notLiveSentence =
    'An alternative internet is not live (alt_internet_live is false). '
    'A packet path is not live (packet_path_live is false). '
    'This isolate cannot see host hardware (worker_hardware is false). '
    'Still missing: a packet that leaves this machine and arrives on a different machine id. '
    'A same-machine mesh frame does not count. '
    'Cap-7 and .aziel stay names, not a public registrar and not ICANN or BGP. '
    'WireGuard, OpenVPN, an L3 exit pool, kernel UDP, and TUN/TAP stay SLOT. '
    'Public mail send, the kernel, and boot stay not live. '
    'The public door stays FG-STUB. '
    'Isolation is single-node security-awareness. '
    'Phoenix is a local wait and re-seal. '
    'That is not a loopback fence.';

const String sameMachineSentence =
    'A second device stays false while both ends share that id.';

const String standSentence =
    'This page stands on its own. Calls to aziel-runtime still use the existing FragGate door. '
    'The domain count stays 33. '
    '$notLiveSentence '
    '$sameMachineSentence '
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
    hint: 'This opens the domain count. software_count stays 33.',
    title: 'Domain count',
    sentences: [
      'The domain count stays 33.',
      'software_count stays 33.',
    ],
  ),
  SentenceControl(
    id: 'mail',
    label: 'Mail',
    hint: 'This opens the mail sentence. Public mail send stays not live.',
    title: 'Mail',
    sentences: [
      'This row is in the catalog. Mail send does not run on the public worker.',
      'Public mail send, the kernel, and boot stay not live.',
    ],
  ),
  SentenceControl(
    id: 'network',
    label: 'Network',
    hint:
        'This opens the network sentence. alt_internet_live is false. packet_path_live is false.',
    title: 'Network',
    sentences: [
      notLiveSentence,
    ],
  ),
  SentenceControl(
    id: 'azos',
    label: 'AZ-OS',
    hint: 'This opens the AZ-OS sentence. The kernel and boot stay not live.',
    title: 'AZ-OS',
    sentences: [
      'This row is in the catalog. The public worker does not run a kernel. Boot does not run on the public worker.',
      'The host operating system stays the host operating system.',
      'Public mail send, the kernel, and boot stay not live.',
      'There is no kernel.',
      'This has not booted.',
    ],
  ),
  SentenceControl(
    id: 'second-device',
    label: 'Another device',
    hint:
        'This opens the second-device sentence. A second device stays false while both ends share that id.',
    title: 'Another device',
    sentences: [
      sameMachineSentence,
      'A same-machine mesh frame does not count.',
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
    'software_count stays $softwareCount.',
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
