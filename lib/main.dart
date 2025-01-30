import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:typed_data';

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
  late Animation<double> _scaleAnimation;
  late Animation<Color?> _colorAnimation;
  late Animation<Offset> _floatingAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 3),
    );

    _scaleAnimation = Tween<double>(begin: 0.9, end: 1.1).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeInOut,
      ),
    );

    _colorAnimation = ColorTween(
      begin: Colors.blueAccent,
      end: Colors.purpleAccent,
    ).animate(_animationController);

    _floatingAnimation = Tween<Offset>(
      begin: const Offset(0, 0),
      end: const Offset(0, -0.1),
    ).animate(
      CurvedAnimation(
        parent: _animationController,
        curve: Curves.easeInOut,
      ),
    );

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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Resume Scanner'),
        centerTitle: true,
        flexibleSpace: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              colors: [Colors.blueAccent, Colors.purpleAccent],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
        ),
        elevation: 10,
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(bottom: Radius.circular(30)),
        ),
      ),
      body: Stack(
        children: [
          // Parallax Background
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _animationController,
              builder: (context, child) {
                return Transform.translate(
                  offset: Offset(0, _floatingAnimation.value.dy * 50),
                  child: Opacity(
                    opacity: 0.3,
                    child: Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [Colors.blue.shade50, Colors.purple.shade50],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
          // Floating Icons
          Positioned(
            top: 100,
            left: 20,
            child: AnimatedBuilder(
              animation: _animationController,
              builder: (context, child) {
                return Transform.translate(
                  offset: Offset(0, _floatingAnimation.value.dy * 20),
                  child: Icon(Icons.description, size: 40, color: Colors.blue.withOpacity(0.5)),
                );
              },
            ),
          ),
          Positioned(
            top: 200,
            right: 30,
            child: AnimatedBuilder(
              animation: _animationController,
              builder: (context, child) {
                return Transform.translate(
                  offset: Offset(0, _floatingAnimation.value.dy * 30),
                  child: Icon(Icons.work, size: 50, color: Colors.purple.withOpacity(0.5)),
                );
              },
            ),
          ),
          Positioned(
            bottom: 100,
            left: 50,
            child: AnimatedBuilder(
              animation: _animationController,
              builder: (context, child) {
                return Transform.translate(
                  offset: Offset(0, _floatingAnimation.value.dy * 40),
                  child: Icon(Icons.cloud_upload, size: 60, color: Colors.blue.withOpacity(0.5)),
                );
              },
            ),
          ),
          // Main Content
          SingleChildScrollView(
            padding: const EdgeInsets.all(30.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.center,
              children: [
                const Text(
                  'Upload your resume',
                  style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.blueGrey),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 10),
                Text(
                  'and let the right job find you!',
                  style: TextStyle(fontSize: 16, color: Colors.grey[700]),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 40),
                AnimatedBuilder(
                  animation: _animationController,
                  builder: (context, child) {
                    return Transform.scale(
                      scale: _scaleAnimation.value,
                      child: Container(
                        width: MediaQuery.of(context).size.width * .8,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            colors: [Colors.blue.shade100, Colors.purple.shade100],
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                          ),
                          borderRadius: BorderRadius.circular(20),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.2),
                              blurRadius: 10,
                              spreadRadius: 2,
                            ),
                          ],
                        ),
                        padding: const EdgeInsets.all(20),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.center,
                          children: [
                            Icon(Icons.upload_file, size: 60, color: _colorAnimation.value),
                            const SizedBox(height: 20),
                            ElevatedButton(
                              onPressed: _isLoading ? null : _pickFile,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: _colorAnimation.value,
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(vertical: 15, horizontal: 30),
                                textStyle: const TextStyle(fontSize: 16),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                elevation: 5,
                              ),
                              child: _isLoading
                                  ? FadeTransition(
                                      opacity: _animationController,
                                      child: const Icon(Icons.cloud_upload, size: 24, color: Colors.white),
                                    )
                                  : const Text('Upload Your Resume'),
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
                const SizedBox(height: 40),
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 500),
                  child: Text(
                    _scanResult,
                    key: ValueKey<String>(_scanResult),
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blueGrey),
                    textAlign: TextAlign.center,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}