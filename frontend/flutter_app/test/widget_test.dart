import 'package:flutter_test/flutter_test.dart';

import 'package:flutter_app/main.dart';

void main() {
  testWidgets('Aether Dev shell renders', (WidgetTester tester) async {
    await tester.pumpWidget(const AetherDevApp());

    expect(find.text('Chat'), findsOneWidget);
    expect(find.text('Runtime'), findsOneWidget);
  });
}
