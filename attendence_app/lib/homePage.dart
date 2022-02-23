import 'dart:convert';
// import 'dart:html';
import 'package:attendence_app/Drawer.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:geolocator/geolocator.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/http.dart' as http;
import 'package:imei_plugin/imei_plugin.dart';
import 'package:permission_handler/permission_handler.dart';

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

bool marked = false;
String lat, lon;
String tok, imei;
String baseUrl = 'https://safe-falls-63951.herokuapp.com';

class annon {
  String announceDate;
  String message;
  annon(this.announceDate, this.message);
}

List<annon> announcementL = [];

Future<String> askPerm() async {
  if (await Permission.locationAlways.isGranted &&
      await Permission.phone.isGranted) {
    return 'ok';
  } else {
    Map<Permission, PermissionStatus> statuses = await [
      Permission.locationAlways,
      Permission.phone,
    ].request();
  }
}

void verifyPerm() async {
  if (await Permission.locationAlways.isGranted &&
      await Permission.phone.isGranted) {
  } else {
    Fluttertoast.showToast(
        msg: 'You need to give location and phone permissions.');
    SystemNavigator.pop();
  }
}

Future<Position> _determinePosition() async {
  bool serviceEnabled;
  LocationPermission permission;

  serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    return Future.error('Location services are disabled.');
  }

  permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.deniedForever) {
    return Future.error(
        'Location permissions are permantly denied, we cannot request permissions.');
  }

  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission != LocationPermission.whileInUse &&
        permission != LocationPermission.always) {
      return Future.error(
          'Location permissions are denied (actual value: $permission).');
    }
  }
  return await Geolocator.getCurrentPosition();
}

Future<String> _markAttendence() async {
  // var body;
  // String imei = '';
  // getIemi().then((String imei1) {imei = imei1});
  // print(imei);
  try {
    var res = await http.post(baseUrl + '/mark_attendence',
        body: {'x': lat, 'y': lon, 'imei': imei},
        headers: {'Authorization': 'Token ' + tok});
    if (res.statusCode == 200) {
      print(res.body);
      return res.body;
    } else {
      return '{\'error\':\'true\'}';
    }
  } catch (e) {
    Fluttertoast.showToast(msg: 'Check your internet connection');
  }
}

class _HomePageState extends State<HomePage> {
  void getAnnouncementOfToday() async {
    try {
      var res = await http.get(baseUrl + '/getAnnouncementOfToday',
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
      }
    } catch (e) {
      Fluttertoast.showToast(msg: 'Check your internet connection');
    }
  }

  void getIemi() async {
    ImeiPlugin.getImei(shouldShowRequestPermissionRationale: false)
        .then((value) {
      // print("ak" + value);
      setState(() {
        imei = value;
      });
    });
    // print(imei);
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

  void checkStatus() async {
    try {
      // String m1;
      // print("777" + tok);
      var res = await http.get(baseUrl + '/checkStatus',
          headers: {'Authorization': 'Token ' + tok}).then((res) {
        var resP = json.decode(res.body);
        // print(resP['message']);
        if (resP['message'] == 'true') {
          setState(() {
            marked = true;
          });
        } else {
          marked = false;
        }
      });
    } catch (e) {
      Fluttertoast.showToast(msg: 'Check your internet connection');
    }
  }

  Future<List<String>> fetchLatLon() async {
    Position position = await _determinePosition();
    String latitude = position.latitude.toString();
    String longitude = position.longitude.toString();
    return [latitude, longitude];
  }

  @override
  void initState() {
    super.initState();
    askPerm().then((value) {
      if (value == 'ok') {
      } else {
        verifyPerm();
      }
    });
    _getToken().then((value) => checkStatus());
    fetchLatLon().then((value) {
      // print(value);
      setState(() {
        lat = value[0];
        lon = value[1];
      });
    }).then((value) {
      getIemi();
      getAnnouncementOfToday();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: DrawerPage(),
      appBar: AppBar(
        elevation: 0,
        actions: [],
        title: Text('Welcome'),
        centerTitle: true,
      ),
      body: Column(
        children: <Widget>[
          Container(
            padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).size.height * 0.05),
            width: MediaQuery.of(context).size.width,
            height: MediaQuery.of(context).size.height * 0.40,
            child: FloatingActionButton.extended(
              backgroundColor: Colors.orange,
              label: Text(
                marked == false ? "Punch in" : "Punch Out",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 30),
              ),
              onPressed: () {
                fetchLatLon().then((value) async {
                  setState(() {
                    lat = value[0];
                    lon = value[1];
                  });
                  try {
                    var resp = await _markAttendence().then((resp) {
                      // print(resp);
                      // print("adfasdfasfasdfasdfasf");
                      var resP = json.decode(resp);

                      if (resP['message'] == 'ok') {
                        Fluttertoast.showToast(
                          msg: 'Done!',
                        );
                        setState(() {
                          marked = !marked;
                        });
                      } else if (resP['message'] == 'imei') {
                        Fluttertoast.showToast(
                          msg: 'Have you changed your phone?',
                        );
                      } else {
                        Fluttertoast.showToast(
                          msg: 'Not allowed',
                        );
                      }
                    });
                  } catch (e) {
                    Fluttertoast.showToast(
                        msg: 'Check your internet connection');
                  }
                });
              },
            ),
            decoration: BoxDecoration(
              color: Colors.blue,
              borderRadius: BorderRadius.vertical(
                bottom: Radius.circular(50.0),
              ),
            ),
          ),
          Container(
            margin: EdgeInsets.only(bottom: 10.0, top: 10.0),
            child: Text(
              "Today's Announcements",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 20,
                color: Colors.black54,
              ),
            ),
            alignment: Alignment.topLeft,
          ),
          Expanded(
            flex: 1,
            child: ListView.builder(
              shrinkWrap: true,
              itemBuilder: (BuildContext context, int index) {
                return Container(
                  margin: EdgeInsets.only(bottom: 3.0, top: 3.0),
                  child: ListTile(
                    // trailing: Text(
                    //   announcementL[index].announceDate,
                    //   style: TextStyle(color: Colors.white),
                    // ),
                    leading: Icon(
                      Icons.notification_important,
                      color: Colors.white,
                    ),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10.0)),
                    tileColor: Colors.blue,
                    title: Text(
                      announcementL.length == 0
                          ? 'No data to show here.'
                          : announcementL[index].message,
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                );
              },
              itemCount: announcementL.length == 0 ? 1 : announcementL.length,
            ),
          ),
        ],
      ),
    );
  }
}
