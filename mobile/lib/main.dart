import 'package:flutter/material.dart';

import 'theme.dart';

void main() {
  runApp(const AzInterfaceApp());
}

class AzInterfaceApp extends StatelessWidget {
  const AzInterfaceApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AZInterface',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const CustodyPage(),
    );
  }
}

class CustodyPage extends StatefulWidget {
  const CustodyPage({super.key});

  @override
  State<CustodyPage> createState() => _CustodyPageState();
}

class _CustodyPageState extends State<CustodyPage> {
  String _state = 'OFF';
  bool _integrity = false;
  bool _living = false;
  String _genesis = '';
  final _witnesses = <String>[];
  final _seed = TextEditingController();

  @override
  void dispose() {
    _seed.dispose();
    super.dispose();
  }

  void _cycle() {
    _living = _state == 'ON' && _integrity;
  }

  void _setStateName(String next) {
    if (next == 'ON' && !_integrity) {
      setState(() {
        _witnesses.insert(0, 'ON refused — need integrity');
      });
      return;
    }
    setState(() {
      if (_state == 'ON' && next != 'ON') {
        _integrity = false;
      }
      _state = next;
      _cycle();
      _witnesses.insert(0, 'site_state $_state living=$_living');
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AZInterface')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Interface is CUSTODY — never Hub.',
            style: TextStyle(color: kGold, fontStyle: FontStyle.italic, fontSize: 16),
          ),
          const SizedBox(height: 8),
          Text('Site state $_state · living $_living · integrity $_integrity'),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              FilledButton(onPressed: () => _setStateName('ON'), child: const Text('ON')),
              OutlinedButton(onPressed: () => _setStateName('OFF'), child: const Text('OFF')),
              OutlinedButton(onPressed: () => _setStateName('FULL_SHUTDOWN'), child: const Text('FULL SHUTDOWN')),
              OutlinedButton(onPressed: () => _setStateName('MEMORIAL'), child: const Text('MEMORIAL')),
            ],
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: () {
              setState(() {
                _integrity = true;
                _cycle();
                _witnesses.insert(0, 'integrity_check ok');
              });
            },
            child: const Text('Integrity check'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _seed,
            decoration: const InputDecoration(labelText: 'One-time username seed'),
          ),
          const SizedBox(height: 8),
          OutlinedButton(
            onPressed: () {
              if (_genesis.isNotEmpty) return;
              final seed = _seed.text;
              _seed.clear();
              setState(() {
                _genesis = seed.hashCode.toRadixString(16);
                _witnesses.insert(0, 'genesis_hash $_genesis');
              });
            },
            child: const Text('Genesis boot (hash only)'),
          ),
          if (_genesis.isNotEmpty) Text('Genesis Hash Key: $_genesis'),
          const SizedBox(height: 12),
          Text(
            _living ? 'AZHome bunker living.' : 'PRE-LOCKED — AZHome does not render as living presence.',
            style: const TextStyle(color: kGold),
          ),
          const SizedBox(height: 12),
          FilledButton(
            onPressed: _living
                ? () {
                    setState(() => _witnesses.insert(0, 'hold metadata only'));
                  }
                : null,
            child: const Text('Hold'),
          ),
          const SizedBox(height: 8),
          OutlinedButton(
            onPressed: _living
                ? () {
                    setState(() => _witnesses.insert(0, 'withdraw metadata only'));
                  }
                : null,
            child: const Text('Withdraw'),
          ),
          const SizedBox(height: 16),
          const Text('Witness list (no vault contents)', style: TextStyle(color: kGold)),
          for (final r in _witnesses.take(12))
            Card(
              margin: const EdgeInsets.only(top: 8),
              child: Padding(
                padding: const EdgeInsets.all(10),
                child: SelectableText(r, style: const TextStyle(fontFamily: 'monospace', fontSize: 12)),
              ),
            ),
        ],
      ),
    );
  }
}
