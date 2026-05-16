import 'package:flutter/material.dart';

import '../models/conversation.dart';
import '../models/message.dart';
import '../services/api_client.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ApiClient api = ApiClient();
  final TextEditingController input = TextEditingController();
  List<Conversation> conversations = [];
  List<ChatMessage> messages = [];
  String? selectedConversationId;
  Map<String, dynamic>? lastTrace;
  bool loading = false;
  String? error;

  @override
  void initState() {
    super.initState();
    loadConversations();
  }

  Future<void> loadConversations() async {
    setState(() => loading = true);
    try {
      final raw = await api.get('/conversations') as List<dynamic>;
      conversations = raw.map((item) => Conversation.fromJson(item)).toList();
      if (selectedConversationId == null && conversations.isNotEmpty) {
        selectedConversationId = conversations.first.id;
        await loadMessages(selectedConversationId!);
      }
      error = null;
    } catch (err) {
      error = err.toString();
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> newConversation() async {
    final created = await api.post('/conversations', {
      'title': 'New Conversation',
    });
    selectedConversationId = created['id'] as String;
    messages = [];
    await loadConversations();
  }

  Future<void> loadMessages(String conversationId) async {
    final raw =
        await api.get('/conversations/$conversationId/messages')
            as List<dynamic>;
    setState(() {
      selectedConversationId = conversationId;
      messages = raw.map((item) => ChatMessage.fromJson(item)).toList();
    });
  }

  Future<void> send() async {
    final text = input.text.trim();
    if (text.isEmpty) return;
    input.clear();
    setState(() => loading = true);
    try {
      final result =
          await api.post('/chat/message', {
                'conversation_id': selectedConversationId,
                'content': text,
              })
              as Map<String, dynamic>;
      selectedConversationId = result['conversation_id'] as String;
      lastTrace = result['developer_trace'] as Map<String, dynamic>;
      await loadMessages(selectedConversationId!);
      await loadConversations();
      error = null;
    } catch (err) {
      error = err.toString();
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        SizedBox(
          width: 280,
          child: Column(
            children: [
              Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    const Expanded(
                      child: Text(
                        'Conversations',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    IconButton(
                      tooltip: 'New conversation',
                      onPressed: newConversation,
                      icon: const Icon(Icons.add),
                    ),
                  ],
                ),
              ),
              const Divider(height: 1),
              Expanded(
                child: ListView.builder(
                  itemCount: conversations.length,
                  itemBuilder: (context, index) {
                    final item = conversations[index];
                    return ListTile(
                      selected: item.id == selectedConversationId,
                      title: Text(
                        item.title,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      subtitle: Text(
                        item.updatedAt,
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      onTap: () => loadMessages(item.id),
                    );
                  },
                ),
              ),
            ],
          ),
        ),
        const VerticalDivider(width: 1),
        Expanded(
          child: Column(
            children: [
              if (error != null)
                MaterialBanner(
                  content: Text(error!),
                  actions: [
                    TextButton(
                      onPressed: () => setState(() => error = null),
                      child: const Text('Dismiss'),
                    ),
                  ],
                ),
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: messages.length,
                  itemBuilder: (context, index) {
                    final message = messages[index];
                    final isUser = message.role == 'user';
                    return Align(
                      alignment: isUser
                          ? Alignment.centerRight
                          : Alignment.centerLeft,
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 720),
                        child: Container(
                          margin: const EdgeInsets.symmetric(vertical: 6),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: isUser
                                ? const Color(0xffdfeeea)
                                : const Color(0xfff1f3f2),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: const Color(0xffd2d8d6)),
                          ),
                          child: Text(message.content),
                        ),
                      ),
                    );
                  },
                ),
              ),
              if (lastTrace != null)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  color: const Color(0xfff7f8f8),
                  child: Text(
                    'Trace: ${lastTrace!['prompt_summary']} / memory: ${lastTrace!['memory_write_decision']}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              const Divider(height: 1),
              Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: input,
                        minLines: 1,
                        maxLines: 4,
                        onSubmitted: (_) => send(),
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          hintText: 'Send a message to Aether Dev',
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton.filled(
                      tooltip: 'Send',
                      onPressed: loading ? null : send,
                      icon: const Icon(Icons.send),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
