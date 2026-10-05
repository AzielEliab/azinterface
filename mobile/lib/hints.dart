import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class Hint {
  const Hint({required this.id, required this.text});

  final String id;
  final String text;
}

class HintBook extends ChangeNotifier {
  HintBook(this._prefs);

  final SharedPreferences _prefs;
  final List<Hint> _queue = [];
  Hint? current;

  bool seen(String id) => _prefs.getBool(_key(id)) ?? false;

  void meet(Hint hint) {
    if (seen(hint.id)) return;
    if (current?.id == hint.id) return;
    if (_queue.any((item) => item.id == hint.id)) return;
    if (current == null) {
      current = hint;
    } else {
      _queue.add(hint);
    }
    notifyListeners();
  }

  Future<void> dismiss() async {
    final hint = current;
    if (hint == null) return;
    await _prefs.setBool(_key(hint.id), true);
    current = _queue.isEmpty ? null : _queue.removeAt(0);
    notifyListeners();
  }

  String _key(String id) => 'hint.$id';
}

class HintScope extends InheritedWidget {
  const HintScope({required this.book, required super.child, super.key});

  final HintBook book;

  static HintBook of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<HintScope>();
    assert(scope != null, 'HintScope is missing');
    return scope!.book;
  }

  @override
  bool updateShouldNotify(HintScope oldWidget) => book != oldWidget.book;
}

class HintHost extends StatefulWidget {
  const HintHost({
    required this.book,
    required this.navigatorKey,
    required this.child,
    super.key,
  });

  final HintBook book;
  final GlobalKey<NavigatorState> navigatorKey;
  final Widget child;

  @override
  State<HintHost> createState() => _HintHostState();
}

class _HintHostState extends State<HintHost> {
  var _open = false;

  @override
  void initState() {
    super.initState();
    widget.book.addListener(_onBook);
    WidgetsBinding.instance.addPostFrameCallback((_) => _onBook());
  }

  @override
  void dispose() {
    widget.book.removeListener(_onBook);
    super.dispose();
  }

  void _onBook() {
    if (_open || !mounted) return;
    final hint = widget.book.current;
    if (hint == null) return;
    if (widget.navigatorKey.currentContext == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) => _onBook());
      return;
    }
    _open = true;
    final text = hint.text;
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      final dialogContext = widget.navigatorKey.currentContext;
      if (dialogContext == null || !dialogContext.mounted) {
        _open = false;
        return;
      }
      await showDialog<void>(
        context: dialogContext,
        barrierDismissible: false,
        builder: (context) {
          return AlertDialog(
            key: const Key('hint-popup'),
            title: const Text('What this control does'),
            content: Text(text),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(context).pop(),
                child: const Text('OK'),
              ),
            ],
          );
        },
      );
      _open = false;
      if (!mounted) return;
      await widget.book.dismiss();
    });
  }

  @override
  Widget build(BuildContext context) => widget.child;
}

class MeetHint extends StatefulWidget {
  const MeetHint({
    required this.id,
    required this.hint,
    required this.child,
    super.key,
  });

  final String id;
  final String hint;
  final Widget child;

  @override
  State<MeetHint> createState() => _MeetHintState();
}

class _MeetHintState extends State<MeetHint> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      HintScope.of(context).meet(Hint(id: widget.id, text: widget.hint));
    });
  }

  @override
  Widget build(BuildContext context) => widget.child;
}
