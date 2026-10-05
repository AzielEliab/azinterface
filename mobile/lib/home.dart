import 'package:flutter/material.dart';

import 'facts.dart';
import 'hints.dart';
import 'theme.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AZInterface')),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: SingleChildScrollView(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Aziel Eliab',
                  style: TextStyle(color: kGold, fontSize: 16),
                ),
                const SizedBox(height: 8),
                const Text('Interface is CUSTODY.'),
                const SizedBox(height: 12),
                const _SentenceCard(text: standSentence),
                const SizedBox(height: 12),
                Text('The page is $siteState.',
                    key: const Key('site-state-sentence')),
                const SizedBox(height: 4),
                Text(
                  'The domain count stays $softwareCount.',
                  key: const Key('software-count-sentence'),
                ),
                const SizedBox(height: 16),
                for (final control in sentenceControls) ...[
                  MeetHint(
                    id: control.id,
                    hint: control.hint,
                    child: SizedBox(
                      width: double.infinity,
                      child: FilledButton(
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute<void>(
                              builder: (_) => FactPage(control: control),
                            ),
                          );
                        },
                        child: Text(control.label),
                      ),
                    ),
                  ),
                  const SizedBox(height: 8),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class FactPage extends StatelessWidget {
  const FactPage({required this.control, super.key});

  final SentenceControl control;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: const MeetHint(
          id: 'back',
          hint: backHint,
          child: BackButton(),
        ),
        title: Text(control.title),
      ),
      body: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              for (final sentence in control.sentences) ...[
                _SentenceCard(text: sentence),
                const SizedBox(height: 12),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

class _SentenceCard extends StatelessWidget {
  const _SentenceCard({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Text(text),
      ),
    );
  }
}
