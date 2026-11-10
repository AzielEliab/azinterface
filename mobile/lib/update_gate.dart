// The phone and desktop shells do not replace their own bundle.
// A resumed frame asks this gate. The gate does not open a socket.
// auto_update stays off. A mesh membership flag is not a carrier.
// Paid satellite relay stays HELD. live stays false.

class UpdateGateResult {
  const UpdateGateResult({
    required this.event,
    required this.code,
    required this.activated,
    required this.verified,
    required this.downloaded,
    required this.selfPatch,
    required this.live,
    required this.membershipOnly,
    required this.platformSignatureBypassed,
  });

  final String event;
  final String code;
  final bool activated;
  final bool verified;
  final bool downloaded;
  final bool selfPatch;
  final bool live;
  final bool membershipOnly;
  final bool platformSignatureBypassed;
}

UpdateGateResult onAppLifecycle(String event) {
  return _gate(event);
}

UpdateGateResult onConnectivity(String event) {
  return _gate(event);
}

UpdateGateResult _gate(String event) {
  return UpdateGateResult(
    event: event,
    code: 'UPDATE-NOT-READY',
    activated: false,
    verified: false,
    downloaded: false,
    selfPatch: false,
    live: false,
    membershipOnly: true,
    platformSignatureBypassed: false,
  );
}
