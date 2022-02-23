import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:fluttertoast/fluttertoast.dart';

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

final _storage = FlutterSecureStorage();
String baseUrl = 'https://safe-falls-63951.herokuapp.com';

Future<String> getToken() async {
  final storage = new FlutterSecureStorage();
  return await storage.read(key: "token");
}

void checkLogin(context) {
  try {
    getToken().then((tok) async {
      var res = await http.get(baseUrl + "/checkLogin",
          headers: {'Authorization': 'Token ' + tok});
      if (res.statusCode == 200) {
        Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
      }
    }).catchError((e) {
      Fluttertoast.showToast(msg: "Error Occured");
    });
  } catch (e) {
    Fluttertoast.showToast(msg: 'Check your internet connection');
  }
}

Future<String> post(String url, String username, String password) async {
  try {
    // url = 'http://10.0.3.2:8000/login';
    var response = await http.post(url, body: {
      'username': username,
      'password': password,
    }).catchError((e) {
      Fluttertoast.showToast(msg: 'Error Occured!');
    });
    if (response.statusCode == 200) {
      return response.body;
    } else {
      Fluttertoast.showToast(msg: 'Invalid credentials');
      return '\'error\':\'true\'';
    }
  } catch (e) {
    Fluttertoast.showToast(msg: 'Check your internet connection');
  }
}

class _LoginPageState extends State<LoginPage> {
  final username = TextEditingController();
  final password = TextEditingController();

  @override
  void dispose() {
    username.dispose();
    password.dispose();
    super.dispose();
  }

  @override
  void initState() {
    super.initState();
    checkLogin(context);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        actions: [],
        title: Text("Company Name"),
        centerTitle: true,
        elevation: 0,
      ),
      body: Stack(
        children: <Widget>[
          Container(
              child: SingleChildScrollView(
            child: Column(
              children: [
                Container(
                  height: MediaQuery.of(context).size.height * 0.25,
                  child: Image(image: AssetImage("images/logo.jpg")),
                  decoration: BoxDecoration(),
                ),
                Container(
                  margin: EdgeInsets.symmetric(vertical: 20),
                  child: TextField(
                    autofocus: true,
                    controller: username,
                    keyboardType: TextInputType.emailAddress,
                    decoration: new InputDecoration(
                      hintText: "email id",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20.0),
                        borderSide: BorderSide(
                          color: Colors.teal,
                        ),
                      ),
                    ),
                  ),
                ),
                Container(
                  margin: EdgeInsets.only(bottom: 20),
                  child: TextField(
                    controller: password,
                    obscureText: true,
                    autocorrect: false,
                    decoration: new InputDecoration(
                      hintText: "password",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(20.0),
                        borderSide: BorderSide(
                          color: Colors.teal,
                        ),
                      ),
                    ),
                  ),
                ),
                FloatingActionButton.extended(
                  label: Text("Login"),
                  onPressed: () async {
                    print('object');
                    var body = await post(
                        baseUrl + '/login', username.text, password.text);
                    var resp = json.decode(body);
                    if (resp['status'] == 'true') {
                      final String key = "token";
                      await _storage
                          .write(key: key, value: resp['data'])
                          .catchError((e) {
                        print(e);
                      });
                      Navigator.pushNamedAndRemoveUntil(
                          context, '/home', (route) => false);
                    }
                  },
                )
              ],
            ),
          ))
        ],
      ),
    );
  }
}
