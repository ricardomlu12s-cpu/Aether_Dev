class Conversation {
  Conversation({
    required this.id,
    required this.title,
    required this.updatedAt,
  });

  final String id;
  final String title;
  final String updatedAt;

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'] as String,
      title: json['title'] as String,
      updatedAt: json['updated_at'] as String,
    );
  }
}
