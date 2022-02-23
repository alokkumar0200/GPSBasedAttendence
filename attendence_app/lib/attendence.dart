import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/http.dart' as http;

class AttendencePage extends StatefulWidget {
  @override
  _AttendencePageState createState() => _AttendencePageState();
}

String tok;
String baseUrl = 'https://safe-falls-63951.herokuapp.com';

class attendence {
  String date;
  String status;
  attendence(this.date, this.status);
}

List<attendence> attendnceL = [];

class _AttendencePageState extends State<AttendencePage> {
  void getAttendenceOfMonth() async {
    try {
      var res = await http.get(baseUrl + '/getAttendenceOfMonth',
          headers: {'Authorization': 'Token ' + tok});
      if (res.statusCode == 200) {
        var body = json.decode(res.body);
        List<attendence> at = [];
        for (var x in body['data']) {
          at.add(new attendence(x['date'], x['status']));
        }
        setState(() {
          attendnceL = at;
        });
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
      getAttendenceOfMonth();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Attendence Log"),
        centerTitle: true,
      ),
      body: ListView.builder(
        itemBuilder: (BuildContext context, int index) {
          return Container(
            margin: EdgeInsets.only(bottom: 3.0, top: 3.0),
            child: ListTile(
              trailing: Text(
                attendnceL.length == 0 ? '' : attendnceL[index].date,
                style: TextStyle(color: Colors.white),
              ),
              leading: Icon(
                Icons.notification_important,
                color: Colors.white,
              ),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10.0)),
              tileColor: attendnceL[index].status == 'present'
                  ? Colors.green
                  : attendnceL[index].status == 'leave'
                      ? Colors.red
                      : Colors.orange,
              title: Text(
                attendnceL.length == 0
                    ? 'No data to show here.'
                    : attendnceL[index].status == 'present'
                        ? 'on time'
                        : attendnceL[index].status,
                style: TextStyle(color: Colors.white),
              ),
            ),
          );
        },
        itemCount: attendnceL.length == 0 ? 1 : attendnceL.length,
      ),
    );
  }
}
