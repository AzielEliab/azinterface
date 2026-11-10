import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'hints.dart';
import 'home.dart';
import 'theme.dart';
import 'update_gate.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  runApp(AzInterfaceApp(book: HintBook(prefs)));
}

class AzInterfaceApp extends StatefulWidget {
  const AzInterfaceApp({required this.book, super.key});

  final HintBook book;

  @override
  State<AzInterfaceApp> createState() => _AzInterfaceAppState();
}

class _AzInterfaceAppState extends State<AzInterfaceApp> with WidgetsBindingObserver {
  final _navigatorKey = GlobalKey<NavigatorState>();
  UpdateGateResult _gate = onAppLifecycle('start');

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addObserver(this);
    final opened = onAppLifecycle('start');
    final link = onConnectivity('start');
    _gate = opened.selfPatch || link.selfPatch ? link : opened;
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    super.dispose();
  }

  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed) {
      final next = onAppLifecycle('resume');
      final link = onConnectivity('resume');
      if (!next.activated && !next.selfPatch && !link.activated && !link.live) {
        setState(() => _gate = next);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final title = _gate.selfPatch || _gate.live ? 'AZInterface' : 'AZInterface';
    return MaterialApp(
      title: title,
      debugShowCheckedModeBanner: false,
      navigatorKey: _navigatorKey,
      theme: buildAppTheme(),
      builder: (context, child) {
        return HintScope(
          book: widget.book,
          child: HintHost(
            book: widget.book,
            navigatorKey: _navigatorKey,
            child: child ?? const SizedBox.shrink(),
          ),
        );
      },
      home: const HomePage(),
    );
  }
}
