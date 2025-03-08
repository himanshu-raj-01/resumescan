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

class _ResumeScannerState extends State<ResumeScanner> {
  String? _fileName;
  Uint8List? _fileBytes;
  bool _isLoading = false;
  String _scanResult = '';

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
      body: Center(
        child: SingleChildScrollView(
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
              Container(
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
                    const Icon(Icons.upload_file, size: 60, color: Colors.blue),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _pickFile,
                      child: const Text("Pick a File"),
                    ),
                    const SizedBox(height: 20),
                    Text(
                      _scanResult,
                      style: const TextStyle(fontSize: 16, color: Colors.black87),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
