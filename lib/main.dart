import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';
import 'chatbot.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Resume Scanner',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        fontFamily: 'Roboto',
      ),
      debugShowCheckedModeBanner: false,
      home: const ResumeScanner(),
    );
  }
}

class ResumeScanner extends StatefulWidget {
  const ResumeScanner({super.key});

  @override
  _ResumeScannerState createState() => _ResumeScannerState();
}

class _ResumeScannerState extends State<ResumeScanner> with SingleTickerProviderStateMixin {
  String? _fileName;
  Uint8List? _fileBytes;
  bool _isLoading = false;
  String _scanResult = '';
  late AnimationController _animationController;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 5),
    );
    _animation = TweenSequence([ 
      TweenSequenceItem(
        tween: Tween<double>(begin: 0.0, end: 5.0).chain(CurveTween(curve: Curves.easeIn)),
        weight: 50.0,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 1.0, end: 5.5).chain(CurveTween(curve: Curves.bounceOut)),
        weight: 30.0,
      ),
      TweenSequenceItem(
        tween: Tween<double>(begin: 0.5, end: 5.0).chain(CurveTween(curve: Curves.elasticInOut)),
        weight: 20.0,
      ),
    ]).animate(_animationController);

    _animationController.repeat(reverse: true);
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> _pickFile() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['pdf', 'docx', 'txt'],
      );

      if (result != null) {
        final file = result.files.first;
        setState(() {
          _fileName = file.name;
          _fileBytes = file.bytes;
        });

        if (_fileBytes != null) {
          await _uploadFile(_fileBytes!, _fileName!);
        } else {
          setState(() {
            _scanResult = "Error: Could not read file bytes.";
          });
        }
      }
    } catch (e) {
      print('Error picking file: $e');
      setState(() {
        _scanResult = 'Error picking file: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
      _animationController.stop();
    }
  }

  Future<void> _uploadFile(Uint8List fileBytes, String fileName) async {
    setState(() {
      _scanResult = "Uploading and processing...";
    });

    final url = Uri.parse('http://127.0.0.1:8000/predict/'); // Replace with your backend URL

    var request = http.MultipartRequest('POST', url);
    request.files.add(http.MultipartFile.fromBytes('file', fileBytes, filename: fileName));

    try {
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        var decodedResponse = jsonDecode(response.body);
        
        // Extracting and formatting the prediction array
        if (decodedResponse.containsKey('result')) {
          var predictions = decodedResponse['result'];
          setState(() {
            _scanResult = "Predictions: ${predictions.toString()}";
          });
        } else {
          setState(() {
            _scanResult = "Unexpected response format.";
          });
        }
      } else {
        setState(() {
          _scanResult = 'Error uploading file: ${response.statusCode}\n${response.body}';
        });
      }
    } catch (e) {
      setState(() {
        _scanResult = 'Error uploading file: $e';
      });
    }
  }

  Widget _buildFeatureRow(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 10),
          Expanded(child: Text(text, style: TextStyle(color: Colors.grey[800]))),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Resume Scanner'),
        centerTitle: true,
        backgroundColor: const Color.fromARGB(255, 137, 185, 240),
        elevation: 0,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(bottom: Radius.circular(30)),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(30.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            const Text(
              'Upload your resume',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color.fromARGB(255, 2, 26, 61)),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 10),
            Text(
              'and let the right job find you!',
              style: TextStyle(fontSize: 16, color: Colors.grey[700]),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 40),
            Container(
              width: MediaQuery.of(context).size.width * .8,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey.shade400, width: 1),
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10, spreadRadius: 1),
                ],
              ),
              padding: const EdgeInsets.all(20),
              child: Column(crossAxisAlignment: CrossAxisAlignment.center, children: [
                Icon(Icons.upload_file, size: 60, color: Colors.grey[600]),
                const SizedBox(height: 20),
                ElevatedButton(
                  onPressed: _isLoading ? null : _pickFile,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF673AB7),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 15, horizontal: 30),
                    textStyle: const TextStyle(fontSize: 16),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: _isLoading
                      ? FadeTransition(
                          opacity: _animation,
                          child: const Icon(Icons.cloud_upload, size: 24, color: Colors.white),
                        )
                      : const Text('Upload Your Resume'),
                ),
              ]),
            ),
            const SizedBox(height: 40),
            Text(
              _scanResult,
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.black),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}
