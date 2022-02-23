import 'package:attendence_app/Drawer.dart';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:fluttertoast/fluttertoast.dart';
import 'package:http/http.dart' as http;
import 'package:imei_plugin/imei_plugin.dart';
// import 'package:syncfusion_flutter_maps/maps.dart';

class MyLocation extends StatefulWidget {
  @override
  _MyLocationState createState() => _MyLocationState();
}

String lat = '', lon = '';
String tok, imei;
String baseUrl = 'https://safe-falls-63951.herokuapp.com';

void updateLoc() async {
  print(lat);
  var res = await http.post(baseUrl + '/update_loc',
      headers: {'Authorization': 'Token ' + tok},
      body: {'y': lon, 'x': lat, 'imei': imei});
  print(lon);
  print('alok');
  if (res.statusCode == 200) {
    Fluttertoast.showToast(msg: 'Location Updated');
  } else {
    Fluttertoast.showToast(msg: 'Error Occured. Restart the app and try again');
  }
}

class _MyLocationState extends State<MyLocation> {
  @override
  void initState() {
    super.initState();
    _getToken();
    getIemi();
    fetchLatLon().then((value) {
      setState(() {
        lat = value[0];
        lon = value[1];
      });
      updateLoc();
    });

    Fluttertoast.showToast(msg: 'ready');
    // getAnnouncementOfToday();
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

  Future<List<String>> fetchLatLon() async {
    Position position = await _determinePosition();
    String latitude = position.latitude.toString();
    String longitude = position.longitude.toString();
    return [latitude, longitude];
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      drawer: DrawerPage(),
      appBar: AppBar(
        elevation: 0,
        actions: [],
        title: Text('My Location'),
        centerTitle: true,
      ),
      body: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Latitude: '),
              Text(lat),
            ],
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Longitude: '),
              Text(lon),
            ],
          ),
          Container(
            margin: EdgeInsets.only(top: 20),
            child: FloatingActionButton.extended(
              label: Text("Update Location"),
              onPressed: () {
                fetchLatLon().then((value) {
                  setState(() {
                    lat = value[0];
                    lon = value[1];
                  });
                  updateLoc();
                });
              },
            ),
          )
        ],
      ),
    );
  }
}
