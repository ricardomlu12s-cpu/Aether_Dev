class ChatMessage {
  ChatMessage({
    required this.id,
    required this.role,
    required this.content,
    required this.createdAt,
  });

  final String id;
  final String role;
  final String content;
  final String createdAt;

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] as String,
      role: json['role'] as String,
      content: json['content'] as String,
      createdAt: json['created_at'] as String,
    );
  }
}
