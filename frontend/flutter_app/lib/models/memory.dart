class MemoryItem {
  MemoryItem({
    required this.id,
    required this.level,
    required this.content,
    required this.summary,
    required this.importanceScore,
    required this.updatedAt,
  });

  final String id;
  final String level;
  final String content;
  final String summary;
  final double importanceScore;
  final String updatedAt;

  factory MemoryItem.fromJson(Map<String, dynamic> json) {
    return MemoryItem(
      id: json['id'] as String,
      level: json['level'] as String,
      content: json['content'] as String,
      summary: json['summary'] as String,
      importanceScore: (json['importance_score'] as num).toDouble(),
      updatedAt: json['updated_at'] as String,
    );
  }
}
