import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../services/api_service.dart';
import '../services/vpn_service.dart';
import '../services/storage_service.dart';
import 'package:url_launcher/url_launcher.dart';

String? extractEndpoint(String c) => RegExp(r'Endpoint\s*=\s*([^\s]+)').firstMatch(c)?.group(1);
class HomeScreen extends StatefulWidget { const HomeScreen({super.key}); @override State<HomeScreen> createState() => _HomeScreenState(); }
class _HomeScreenState extends State<HomeScreen> {
  final _ctrl = TextEditingController(); bool _conn=false, _loading=false; int _rem=1024, _tot=1024, _spd=1; DateTime? _exp; Timer? _t;
  @override void dispose() { _ctrl.dispose(); _t?.cancel(); super.dispose(); }
  @override void initState() { super.initState(); _checkUpdate(); }
  @override Widget build(BuildContext context) => Scaffold(appBar: AppBar(title: Text('🦅 Raven VPN'), centerTitle: true, backgroundColor: Color(0xFF1e3c72)), body: Padding(padding: EdgeInsets.all(20), child: Column(children: [
    Center(child: Column(children: [Icon(Icons.vpn_lock, size:64, color: Color(0xFF10b981)), SizedBox(height:16), Text('Enter Code', style: TextStyle(fontSize:20, fontWeight: FontWeight.bold)), SizedBox(height:8), Text('From SMS or PWA', style: TextStyle(color: Colors.grey))])), SizedBox(height:32),
    TextField(controller: _ctrl, maxLength: 11, textAlign: TextAlign.center, style: TextStyle(fontSize:24, letterSpacing:2, fontFamily:'monospace'), decoration: InputDecoration(hintText:'RVN-XXXXXXX', counterText:'', border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)), focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide(color: Color(0xFF3b82f6), width:2)))),
    SizedBox(height:24),
    ElevatedButton(onPressed: _loading||_conn?null:_connect, style: ElevatedButton.styleFrom(backgroundColor: _conn?Colors.grey:Color(0xFF10b981), padding: EdgeInsets.symmetric(vertical:16), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))), child: _loading?SizedBox(width:24,height:24,child:CircularProgressIndicator(strokeWidth:2,color:Colors.white)):Text(_conn?'Connected':'🔌 Connect', style: TextStyle(fontSize:16, fontWeight: FontWeight.bold))),
    if(_conn)...[SizedBox(height:16), Container(padding: EdgeInsets.all(16), decoration: BoxDecoration(color: Color(0xFF064e3b), borderRadius: BorderRadius.circular(12), border: Border.all(color: Color(0xFF10b981))), child: Column(children: [Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text('Status:', style: TextStyle(color: Colors.grey)), Text('🟢 Active', style: TextStyle(color: Color(0xFF10b981)))]), SizedBox(height:8), Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text('Data:', style: TextStyle(color: Colors.grey)), Text('$_rem / $_tot MB')]), Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text('Speed:', style: TextStyle(color: Colors.grey)), Text('$_spd Mbps')]), if(_exp!=null)...[SizedBox(height:4), Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text('Expires:', style: TextStyle(color: Colors.grey)), Text('${_exp!.difference(DateTime.now()).inHours}h ${_exp!.difference(DateTime.now()).inMinutes%60}m')])])), OutlinedButton(onPressed: _disconnect, style: OutlinedButton.styleFrom(foregroundColor: Colors.red, side: BorderSide(color: Colors.red)), child: Text('🔌 Disconnect'))],
    Spacer(), Center(child: Text('Need code? Visit ravenstudent.com', style: TextStyle(color: Colors.grey[600], fontSize:12)))
  ])));
  Future<void> _connect() async {
    final c = _ctrl.text.trim().toUpperCase();
    if(!RegExp(r'^[A-Z]{3}-[A-Z0-9]{7}$').hasMatch(c)) return ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Invalid format')));
    setState(()=>_loading=true);
    try{ final r=await ApiService.activateVoucher(c); await StorageService.saveJwtToken(r['access_token']);
    await Clipboard.setData(ClipboardData(text:c)); ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Row(children:[Icon(Icons.check_circle),SizedBox(width:8),Text('Copied!')]), backgroundColor: Color(0xFF10b981)));
    final ep=extractEndpoint(r['config'])??'raven-vpn.yourdomain.com:51820'; await VpnService.connect(r['config'], ep);
    setState(()=>_conn=true,_loading=false,_rem=r['remaining_mb']??1024,_tot=r['total_mb']??1024,_spd=r['speed_mbps']??1,_exp=r['expires_at']!=null?DateTime.parse(r['expires_at']):null);
    }catch(e){setState(()=>_loading=false); ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Failed: $e')));}
  }
  Future<void> _disconnect() async { final t=await StorageService.getJwtToken(); if(t!=null) await ApiService.disconnectSession(t); await VpnService.disconnect(); setState(()=>_conn=false); }
  Future<void> _checkUpdate() async { try{final v=await ApiService.checkVersion(); if(v['latest']!='1.0.0') launchUrl(Uri.parse(v['download_url']));}catch{}}
}
