import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import 'package:fluttertoast/fluttertoast.dart';

class DrawerPage extends StatefulWidget {
  @override
  _DrawerPageState createState() => _DrawerPageState();
}

class profile {
  String username;
  String present;
  String halfday;
  String leave;
  String photo;
  profile(this.username, this.present, this.halfday, this.leave, this.photo);
}

bool present = true;
bool requested = false;
String tok;
String baseUrl = 'https://safe-falls-63951.herokuapp.com';
var profData = profile('username', '0', '0', '0', 'null');

class _DrawerPageState extends State<DrawerPage> {
  void getProfile() async {
    try {
      var res = await http.get(baseUrl + "/getProfile",
          headers: {'Authorization': 'Token ' + tok});
      if (res.statusCode == 200) {
        var body = json.decode(res.body);
        setState(() {
          profData.username = body['username'];
          profData.present = body['present'].toString();
          profData.halfday = body['halfday'].toString();
          profData.leave = body['leave'].toString();
          profData.photo = body['photo'].toString();
        });
      } else {
        Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
      }
    } catch (e) {
      Fluttertoast.showToast(msg: 'Check your internet connection');
    }
  }

  void checkReq() async {
    try {
      var res = await http.get(baseUrl + '/checkRequest',
          headers: {'Authorization': 'Token ' + tok});
      if (res.statusCode == 200) {
        var body = json.decode(res.body);
        if (body['message'] == 'requested') {
          setState(() {
            requested = true;
          });
          // Fluttertoast.showToast(msg: 'Requested for change');
        } else {
          setState(() {
            requested = false;
          });
        }
      }
    } catch (e) {
      Fluttertoast.showToast(msg: 'Check your internet connection');
    }
  }

  void getTodayAttendence() async {
    try {
      var res = await http.get(baseUrl + '/getTodayAttendence',
          headers: {'Authorization': 'Token ' + tok});
      if (res.statusCode == 200) {
        var body = json.decode(res.body);
        if (body['message'] == 'present') {
          setState(() {
            present = true;
          });
          // Fluttertoast.showToast(msg: 'Requested for change');
        } else {
          setState(() {
            present = false;
          });
        }
      }
    } catch (e) {
      Fluttertoast.showToast(msg: 'Check your internet connection');
    }
  }

  void reqAttendenceChange() async {
    // int i=1;
    try {
      var res = await http.get(baseUrl + '/reqAttendenceChange',
          headers: {'Authorization': 'Token ' + tok});
      if (res.statusCode == 200) {
        var body = json.decode(res.body);
        if (body['message'] == 'done') {
          setState(() {
            requested = true;
          });
          Fluttertoast.showToast(msg: 'Done');
        } else {
          Fluttertoast.showToast(msg: 'Can\'t do that.');
        }
      } else {
        Navigator.pushNamedAndRemoveUntil(context, '/', (route) => false);
      }
    } catch (e) {
      Fluttertoast.showToast(msg: 'Check your internet connection');
    }
  }

  Future<String> _getToken() async {
    final storage = new FlutterSecureStorage();
    var tok1 = await storage.read(key: "token");
    // print(tok1);
    setState(() {
      tok = tok1;
    });
    // print(tok);
  }

  @override
  void initState() {
    super.initState();
    _getToken().then((value) {
      checkReq();
      getTodayAttendence();
      getProfile();
    });

    print("123");
  }

  @override
  Widget build(BuildContext context) {
    return Drawer(
      // Add a ListView to the drawer. This ensures the user can scroll
      // through the options in the drawer if there isn't enough vertical
      // space to fit everything.
      child: ListView(
        // Important: Remove any padding from the ListView.
        padding: EdgeInsets.zero,
        children: <Widget>[
          DrawerHeader(
            child: Row(
              children: [
                CircleAvatar(
                  child: ClipOval(
                    child: FadeInImage(
                      fit: BoxFit.cover,
                      image: profData.photo == 'null'
                          ? AssetImage('images/logo.jpg')
                          : NetworkImage(baseUrl + profData.photo),
                      placeholder: AssetImage('images/logo.jpg'),
                    ),
                  ),
                  radius: 50.0,
                ),
                Expanded(
                  flex: 1,
                  child: Container(
                    // width: MediaQuery.of(context).size.width,
                    margin: EdgeInsets.only(left: 5.0),
                    child: Column(
                      children: [
                        Text(
                          profData.username,
                          style: TextStyle(
                            color: Colors.white,
                          ),
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            Text(
                              "Present:",
                              style: TextStyle(
                                color: Colors.white,
                              ),
                            ),
                            Text(
                              profData.present,
                              style: TextStyle(
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            Text(
                              "Half Days:",
                              style: TextStyle(
                                color: Colors.white,
                              ),
                            ),
                            Text(
                              profData.halfday,
                              style: TextStyle(
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            Text(
                              "Leave:",
                              style: TextStyle(
                                color: Colors.white,
                              ),
                            ),
                            Text(
                              profData.leave,
                              style: TextStyle(
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                        Container(
                          margin: EdgeInsets.only(top: 7),
                          child: FloatingActionButton.extended(
                            backgroundColor:
                                present == true ? Colors.green : Colors.orange,
                            label: Text(
                              present == true
                                  ? "Present"
                                  : requested == true
                                      ? "Pending"
                                      : "Request a change.",
                              style: TextStyle(
                                  fontWeight: FontWeight.bold, fontSize: 12),
                            ),
                            onPressed: present == true && requested == false
                                ? () => {
                                      Fluttertoast.showToast(
                                          msg: 'Can\'t Request.')
                                    }
                                : () {
                                    reqAttendenceChange();
                                    // Fluttertoast.showToast(msg: 'Done');
                                  },
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
            decoration: BoxDecoration(
              color: Colors.blue,
            ),
          ),
          ListTile(
            title: Text('Announcements'),
            onTap: () {
              Navigator.pushNamed(context, '/announcement');
            },
          ),
          ListTile(
            title: Text('Attendence'),
            onTap: () {
              Navigator.pushNamed(context, '/attendence');
            },
          ),
          ListTile(
            title: Text('Personal Messages'),
            onTap: () {
              Navigator.pushNamed(context, '/messages');
            },
          ),
          ListTile(
            title: Text('My Location'),
            onTap: () {
              Navigator.pushNamed(context, '/loc');
            },
          ),
        ],
      ),
    );
  }
}
