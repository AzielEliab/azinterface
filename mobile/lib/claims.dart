// Fails closed when a sentence says a refused door is live.

class LiveTopic {
  const LiveTopic(this.name, this.topic, this.live);

  final String name;
  final RegExp topic;
  final RegExp live;
}

final RegExp _negation = RegExp(
  r"\b(not|never|without|absent|refused|cannot|can't)\b",
  caseSensitive: false,
);

final List<LiveTopic> liveTopics = [
  LiveTopic(
    'public mail send',
    RegExp(r'public mail send|mail send', caseSensitive: false),
    RegExp(r'\b(is live|are live|runs|is running|does run|live)\b',
        caseSensitive: false),
  ),
  LiveTopic(
    'packet path',
    RegExp(r'packet path', caseSensitive: false),
    RegExp(r'\b(is live|are live|runs|is running|does run|live)\b',
        caseSensitive: false),
  ),
  LiveTopic(
    'alternative internet',
    RegExp(r'alternative internet', caseSensitive: false),
    RegExp(r'\b(is live|are live|runs|is running|does run|live)\b',
        caseSensitive: false),
  ),
  LiveTopic(
    'kernel',
    RegExp(r'\bkernel\b', caseSensitive: false),
    RegExp(r'\b(is live|are live|runs|is running|does run|live)\b',
        caseSensitive: false),
  ),
  LiveTopic(
    'boot',
    RegExp(r'\bboot(?:ed|s|ing)?\b', caseSensitive: false),
    RegExp(
        r'\b(is live|are live|runs|is running|does run|has booted|boots|live)\b',
        caseSensitive: false),
  ),
  LiveTopic(
    'second device',
    RegExp(r'second device|another device', caseSensitive: false),
    RegExp(r'\b(is live|are live|runs|is running|wipes?|live)\b',
        caseSensitive: false),
  ),
];

List<String> liveClaims(String text) {
  final found = <String>[];
  for (final sentence in text.split(RegExp(r'[.!?\n;]'))) {
    for (final topic in liveTopics) {
      if (topic.topic.hasMatch(sentence) &&
          topic.live.hasMatch(sentence) &&
          !_negation.hasMatch(sentence)) {
        found.add(topic.name);
      }
    }
  }
  return found;
}
