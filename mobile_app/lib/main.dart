import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

// ملاحظة: لدعم الإشعارات في الخلفية (Background Push Notifications)،
// سيتم دمج مكتبة `flutter_local_notifications` و `workmanager`
// لضمان اتصال WebSocket وإطلاق التنبيهات حتى عند إغلاق التطبيق.
// تم تجهيز البنية التحتية لاستقبالها كـ Local Notification هنا.

void main() => runApp(const SmartGymApp());

class SmartGymApp extends StatelessWidget {
  const SmartGymApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Smart Gym AI',
      theme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: const Color(0xFF0F172A), // Modern Dark Slate
      ),
      home: const AthleteDashboard(userId: 1),
    );
  }
}

class AthleteDashboard extends StatefulWidget {
  final int userId;
  const AthleteDashboard({super.key, required this.userId});

  @override
  State<AthleteDashboard> createState() => _AthleteDashboardState();
}

class _AthleteDashboardState extends State<AthleteDashboard> {
  late WebSocketChannel _channel;
  List<String> _alerts = [];

  @override
  void initState() {
    super.initState();
    // Connect to the WebSocket Endpoint
    // Use 10.0.2.2 for Android emulator to connect to localhost
    _channel = WebSocketChannel.connect(
      Uri.parse('ws://10.0.2.2:8000/ws/alerts/${widget.userId}'),
    );

    // Listen to incoming messages from the AI backend
    _channel.stream.listen((message) {
      final data = jsonDecode(message);
      if (data['type'] == 'URGENT_ALERT') {
        setState(() {
          _alerts.insert(0, "${data['message']}\nالتوصية: ${data['recommendation']}");
        });
        _showDangerAlert(data['message'], data['recommendation']);
      }
    });
  }

  void _showDangerAlert(String msg, String rec) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: Colors.redAccent.withOpacity(0.9),
        title: const Text("⚠️ تنبيه خطر", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        content: Text("$msg\n\n$rec", style: const TextStyle(color: Colors.white)),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text("استُلم", style: TextStyle(color: Colors.white)),
          )
        ],
      ),
    );
  }

  @override
  void dispose() {
    _channel.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Smart Dashboard'),
        backgroundColor: const Color(0xFF1E293B),
        centerTitle: true,
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Card(
              color: Color(0xFF334155),
              child: Padding(
                padding: EdgeInsets.all(16.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text("الحالة الحالية", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                    Icon(Icons.monitor_heart, color: Colors.greenAccent, size: 30),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 10),
            // رسوم الأداء البيانية (Performance Metrics Graphs)
            Card(
              color: const Color(0xFF1E293B),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    const Text("مؤشرات الأداء", style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blueAccent)),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        const Text("Endurance:", style: TextStyle(color: Colors.white70)),
                        const SizedBox(width: 10),
                        Expanded(child: LinearProgressIndicator(value: 0.75, backgroundColor: Colors.grey[800], color: Colors.greenAccent)),
                      ],
                    ),
                    const SizedBox(height: 10),
                    Row(
                      children: [
                        const Text("Recovery Rate:", style: TextStyle(color: Colors.white70)),
                        const SizedBox(width: 10),
                        Expanded(child: LinearProgressIndicator(value: 0.40, backgroundColor: Colors.grey[800], color: Colors.orangeAccent)),
                      ],
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Align(
              alignment: Alignment.centerRight,
              child: Text("سجل التنبيهات اللحظية:", style: TextStyle(fontSize: 18, color: Colors.blueAccent)),
            ),
            const SizedBox(height: 10),
            Expanded(
              child: ListView.builder(
                itemCount: _alerts.length,
                itemBuilder: (context, index) {
                  return Card(
                    color: Colors.red[900]?.withOpacity(0.5),
                    child: ListTile(
                      leading: const Icon(Icons.warning_amber_rounded, color: Colors.orange),
                      title: Text(_alerts[index], style: const TextStyle(fontSize: 14)),
                    ),
                  );
                },
              ),
            )
          ],
        ),
      ),
    );
  }
}

// ==========================================
// واجهة المدرب (Coach UI) - Team Analytics
// ==========================================
class CoachDashboard extends StatefulWidget {
  const CoachDashboard({super.key});

  @override
  State<CoachDashboard> createState() => _CoachDashboardState();
}

class _CoachDashboardState extends State<CoachDashboard> {
  // يفترض جلب البيانات من /coach/team-analytics
  List<Map<String, dynamic>> _teamRisks = [
    {"name": "أحمد", "hr": 165, "risk": "High", "fatigue": "High"},
    {"name": "سالم", "hr": 105, "risk": "Low", "fatigue": "Low"},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('تحليلات الفريق - المدرب'),
        backgroundColor: Colors.indigo[900],
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _teamRisks.length,
        itemBuilder: (context, index) {
          final player = _teamRisks[index];
          final isHighRisk = player['risk'] == 'High';
          return Card(
            color: isHighRisk ? Colors.red[900]?.withOpacity(0.7) : Colors.green[900]?.withOpacity(0.5),
            child: ListTile(
              title: Text(player['name'] + " (نبض: ${player['hr']})", style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text("مؤشر الخطر: ${player['risk']} | الإرهاق: ${player['fatigue']}"),
              trailing: isHighRisk ? const Icon(Icons.warning, color: Colors.yellow) : const Icon(Icons.check_circle, color: Colors.greenAccent),
            ),
          );
        },
      ),
    );
  }
}
