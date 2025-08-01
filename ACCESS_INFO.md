# SafeData Pipeline - Access Information

## Web Interface (Streamlit)
- **Replit URL**: https://workspace.replit30tousebr.repl.co
- **Local Network**: http://172.31.100.34:5000
- **Localhost**: http://localhost:5000
- **All Interfaces**: http://0.0.0.0:5000

## Desktop Application (GUI)
- Run: `python gui_app.py`
- Full desktop interface with all features

## For VSCode/Local Development:
The Streamlit app is configured to run on:
- Port: 5000
- Address: 0.0.0.0 (binds to ALL network interfaces - like React apps)
- Accessible from ANY IP address on port 5000

Access URLs (should work from any machine on the network):
1. http://172.31.100.34:5000 (server IP)
2. http://localhost:5000 (local access)
3. http://127.0.0.1:5000 (loopback)
4. http://[YOUR_LOCAL_IP]:5000 (from other machines)
5. https://workspace.replit30tousebr.repl.co (Replit web URL)

The app now behaves like React development servers - accessible from any IP!

## Test Data
- Use `test_dataset_sample.csv` for testing
- Sample has 1000 records with proper privacy testing scenarios

## Status
✅ Web interface running on port 5000
✅ GUI application fully functional
✅ All core modules tested and working
✅ Ready for production use