// import 'package:attendence_app/homePage.dart';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/http.dart' as http;

class AnnouncementPage extends StatefulWidget {
  @override
  _AnnouncementPageState createState() => _AnnouncementPageState();
}

String tok;
String baseUrl = 'https://safe-falls-63951.herokuapp.com';

class annon {
  String announceDate;
  String message;
  annon(this.announceDate, this.message);
}

List<annon> announcementL = [];

class _AnnouncementPageState extends State<AnnouncementPage> {
  void getAnnouncementOfMonth() async {
    try {
      var res = await http.get(baseUrl + '/getAnnouncementOfMonth',
          headers: {'Authorization': 'Token ' + tok});
      if (res.statusCode == 200) {
        List<annon> t1 = [];
        var body = json.decode(res.body);
        for (var x in body['data']) {
          t1.add(annon(x['date'], x['txt']));
        }
        setState(() {
          announcementL = t1;
        });
      } else {
        Fluttertoast.showToast(msg: 'No data to show here');
      }
    } catch (e) {
      print('Check your internet connection');
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
      getAnnouncementOfMonth();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        title: Text("Announcements"),
        centerTitle: true,
      ),
      body: ListView.builder(
        itemBuilder: (BuildContext context, int index) {
          return Container(
            margin: EdgeInsets.only(bottom: 3.0, top: 3.0),
            child: ListTile(
              trailing: Text(
                announcementL.length == 0
                    ? ''
                    : announcementL[index].announceDate,
                style: TextStyle(color: Colors.white),
              ),
              leading: Icon(
                Icons.notification_important,
                color: Colors.white,
              ),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10.0)),
              tileColor: Colors.blue,
              title: Text(
                announcementL.length == 0
                    ? 'No data to show here'
                    : announcementL[index].message,
                style: TextStyle(color: Colors.white),
              ),
            ),
          );
        },
        itemCount: announcementL.length == 0 ? 1 : announcementL.length,
      ),
    );
  }
}
