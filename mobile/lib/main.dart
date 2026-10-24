import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'hints.dart';
import 'home.dart';
import 'theme.dart';

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

class _AzInterfaceAppState extends State<AzInterfaceApp> {
  final _navigatorKey = GlobalKey<NavigatorState>();

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'AZInterface',
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
