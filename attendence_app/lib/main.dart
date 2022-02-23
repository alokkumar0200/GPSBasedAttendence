import 'package:attendence_app/Announcement.dart';
import 'package:attendence_app/attendence.dart';
import 'package:attendence_app/location.dart';
import 'package:attendence_app/message.dart';
import 'package:flutter/material.dart';
import 'package:attendence_app/login.dart';
import 'package:attendence_app/homePage.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      routes: {
        '/': (context) => LoginPage(),
        '/home': (context) => HomePage(),
        '/announcement': (context) => AnnouncementPage(),
        '/attendence': (context) => AttendencePage(),
        '/messages': (context) => Messages(),
        '/loc': (context) => MyLocation(),
      },
      title: 'Flutter Demo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      // home: MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}
