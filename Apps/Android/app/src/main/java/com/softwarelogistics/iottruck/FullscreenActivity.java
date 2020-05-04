package com.softwarelogistics.iottruck;

import android.Manifest;
import android.annotation.SuppressLint;

import androidx.appcompat.app.ActionBar;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.bluetooth.BluetoothAdapter;
import android.bluetooth.BluetoothDevice;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.util.Log;
import android.view.Menu;
import android.view.MotionEvent;
import android.view.View;
import android.widget.AdapterView;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import java.lang.ref.WeakReference;

/**
 * An example full-screen activity that shows and hides the system UI (i.e.
 * status bar and navigation/system bar) with user interaction.
 */
public class FullscreenActivity extends AppCompatActivity {

    BluetoothService mBluetoothService;
    BluetoothDeviceAdapter bluetoothDevicesAdapter;

    LinearLayout mParkingView;
    ProgressBar pkSensor1;
    ProgressBar pkSensor2;
    ProgressBar pkSensor3;
    ProgressBar pkSensor4;
    ProgressBar pkSensor5;
    ProgressBar pkSensor6;
    ProgressBar pkSensor7;
    ProgressBar pkSensor8;
    ProgressBar lidar;

    TextView txtSensor1;
    TextView txtSensor2;
    TextView txtSensor3;
    TextView txtSensor4;
    TextView txtSensor5;
    TextView txtSensor6;
    TextView txtSensor7;
    TextView txtSensor8;
    TextView txtLidar;

    LinearLayout mDeviceSearchView;
    Button mSearchNow;
    ListView mDeviceList;

    public static String TAG = "IOTTRUCK.ParkingSensor";

    /**
     * Some older devices needs a small delay between UI widget updates
     * and a change of the status and navigation bar.
     */
    private static final int UI_ANIMATION_DELAY = 300;
    private final Handler mHideHandler = new Handler();
    private View mContentView;
    private final Runnable mHidePart2Runnable = new Runnable() {
        @SuppressLint("InlinedApi")
        @Override
        public void run() {
            // Delayed removal of status and navigation bar

            // Note that some of these constants are new as of API 16 (Jelly Bean)
            // and API 19 (KitKat). It is safe to use them, as they are inlined
            // at compile-time and do nothing on earlier devices.
            mContentView.setSystemUiVisibility(View.SYSTEM_UI_FLAG_LOW_PROFILE
                    | View.SYSTEM_UI_FLAG_FULLSCREEN
                    | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                    | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                    | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                    | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION);
        }
    };

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_fullscreen);

        mDeviceSearchView = findViewById(R.id.device_search_view);
        mDeviceList = findViewById(R.id.device_list);
        mSearchNow = findViewById(R.id.search_now);

        bluetoothDevicesAdapter = new BluetoothDeviceAdapter(this);
        mDeviceList.setAdapter(bluetoothDevicesAdapter);

        findViewById(R.id.search_now).setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                startSearching();
            }
        });

        mDeviceList.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {
                selectBlueToothItem(position);
            }
        });

        mParkingView = findViewById(R.id.parking_view);

        pkSensor1 = findViewById(R.id.pk_sensor1);
        pkSensor2 = findViewById(R.id.pk_sensor2);
        pkSensor3 = findViewById(R.id.pk_sensor3);
        pkSensor4 = findViewById(R.id.pk_sensor4);
        pkSensor5 = findViewById(R.id.pk_sensor5);
        pkSensor6 = findViewById(R.id.pk_sensor6);
        pkSensor7 = findViewById(R.id.pk_sensor7);
        pkSensor8 = findViewById(R.id.pk_sensor8);
        lidar = findViewById(R.id.lidar);

        txtSensor1 = findViewById(R.id.pk_sensor1_lbl);
        txtSensor2 = findViewById(R.id.pk_sensor2_lbl);
        txtSensor3 = findViewById(R.id.pk_sensor3_lbl);
        txtSensor4 = findViewById(R.id.pk_sensor4_lbl);
        txtSensor5 = findViewById(R.id.pk_sensor5_lbl);
        txtSensor6 = findViewById(R.id.pk_sensor6_lbl);
        txtSensor7 = findViewById(R.id.pk_sensor7_lbl);
        txtSensor8 = findViewById(R.id.pk_sensor8_lbl);

        txtLidar = findViewById(R.id.lidar_lbl);
    }

    boolean mHasBluetoothPermissions;
    boolean mHasBluetoothAdminPermissions;

    private static final int REQUEST_PERMISSIONS = 1;
    private static String[] APP_PERMISSIONS = {
            Manifest.permission.BLUETOOTH,
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.BLUETOOTH_ADMIN
    };

    public void verifyAppPermissions() {
        // Check if we have write permission
        boolean hasAll = true;
        mHasBluetoothPermissions = ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH) == PackageManager.PERMISSION_GRANTED;
        mHasBluetoothAdminPermissions = ActivityCompat.checkSelfPermission(this, Manifest.permission.BLUETOOTH_ADMIN) == PackageManager.PERMISSION_GRANTED;
        hasAll &= ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED;
        hasAll &= ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) == PackageManager.PERMISSION_GRANTED;

        if (!hasAll) {
            // We don't have permission so prompt the user
            ActivityCompat.requestPermissions(
                    this,
                    APP_PERMISSIONS,
                    REQUEST_PERMISSIONS
            );
        }
    }

    @Override protected void onStart() {
        super.onStart();

        IntentFilter filter = new IntentFilter();
        filter.addAction(BluetoothDevice.ACTION_FOUND);
        filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED);
        filter.addAction(BluetoothAdapter.ACTION_STATE_CHANGED);
        registerReceiver(mReceiver, filter);

        this.verifyAppPermissions();
    }

    @Override protected void onStop() {
        super.onStop();
        Log.d(FullscreenActivity.TAG, "Receiver unregistered");
        unregisterReceiver(mReceiver);
    }

    void showSearchView() {
        mDeviceSearchView.setVisibility(View.VISIBLE);
        mBluetoothService.disconnect();
        mBluetoothService = null;
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        switch (requestCode) {
            case REQUEST_PERMISSIONS: {
                for(int idx = 0; idx < permissions.length; ++idx) {
                    //YUCK THERE HAS TO BE A BETTER WAY!
                    if(permissions[idx].contentEquals(Manifest.permission.BLUETOOTH) &&
                            grantResults[idx] == PackageManager.PERMISSION_GRANTED) {
                        mHasBluetoothPermissions = true;
                    }

                    if(permissions[idx].contentEquals(Manifest.permission.BLUETOOTH_ADMIN) &&
                            grantResults[idx] == PackageManager.PERMISSION_GRANTED) {
                        mHasBluetoothAdminPermissions = true;
                    }
                }
            }
        }
    }

    void selectBlueToothItem(int idx) {
        BluetoothDevice device = bluetoothDevicesAdapter.getItem(idx);

     //   mBluetoothAddress.setText(device.getAddress());

        mBluetoothMessageHandler = new BluetoothMessageHandler(FullscreenActivity.this);
        mBluetoothService = new BluetoothService(mBluetoothMessageHandler, device);
        mBluetoothService.connect();

        mBluetoothMessageHandler = new BluetoothMessageHandler(FullscreenActivity.this);
    }

    private void enableBluetooth(){
        Log.d(TAG, "Enabling Bluetooth");

        Intent enableBtIntent = new Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE);
        startActivityForResult(enableBtIntent, Constants.REQUEST_ENABLE_BT);
    }

    private void startSearching(){
        enableBluetooth();
        Log.d(TAG, "Start Searching" + String.format("%d", (int)(38.23 % 12.0)));
        bluetoothDevicesAdapter.clear();

        BluetoothAdapter bluetoothAdapter = BluetoothAdapter.getDefaultAdapter();
        if(bluetoothAdapter.isEnabled()) {
            if(bluetoothAdapter == null) {
                Toast.makeText(this, "No bluetooth adapter found", Toast.LENGTH_SHORT).show();
            }
            else {
                if(!bluetoothAdapter.startDiscovery()) {
                    Toast.makeText(this, "Failed to start searching", Toast.LENGTH_SHORT).show();
                }
                else {
                    Toast.makeText(this, "Searching for NuvIoT devices.", Toast.LENGTH_SHORT).show();
                    mSearchNow.setEnabled(false);
                }
            }
        }
        else {
            enableBluetooth();
            Toast.makeText(this, "Enabling Bluetooth", Toast.LENGTH_SHORT).show();
        }
    }

    BluetoothMessageHandler mBluetoothMessageHandler;

    private void queryDevice() {
        mBluetoothService.write("HELLO\n".getBytes());
        mBluetoothService.write("QUERY\n".getBytes());
    }

    float _pkSensor1;
    float _pkSensor2;
    float _pkSensor3;
    float _pkSensor4;
    float _pkSensor5;
    float _pkSensor6;
    float _pkSensor7;
    float _pkSensor8;

    float _lidarDistance;
    float _lidarSignalStrength;

    private class BluetoothMessageHandler extends Handler {

        private final WeakReference<FullscreenActivity> mActivity;

        public BluetoothMessageHandler(FullscreenActivity activity) {
            mActivity = new WeakReference<>(activity);
        }

        @Override
        public void handleMessage(Message msg) {
            switch (msg.what) {
                case Constants.MESSAGE_STATE_CHANGE:
                    switch (msg.arg1) {
                        case Constants.STATE_CONNECTED:
                            Toast.makeText(FullscreenActivity.this, "Bluetooth connected", Toast.LENGTH_SHORT).show();
                            queryDevice();

                            mParkingView.setVisibility(View.VISIBLE);
                            mDeviceSearchView.setVisibility(View.GONE);;

                            break;
                        case Constants.STATE_CONNECTING:
                            Toast.makeText(FullscreenActivity.this, "Bluetooth connecting", Toast.LENGTH_SHORT).show();
                            break;
                        case Constants.STATE_NONE:
                            Log.d(TAG, "No devices found.");
                            break;
                        case Constants.STATE_DISCONNECTED:
                            Toast.makeText(FullscreenActivity.this, "Bluetooth Disconnected", Toast.LENGTH_SHORT).show();
                            //mDeviceEditor.setVisibility(View.GONE);
                            mDeviceSearchView.setVisibility(View.VISIBLE);
                            mBluetoothService = null;
                            startSearching();
                            break;
                        case Constants.STATE_ERROR:
                            Toast.makeText(FullscreenActivity.this, "Error Connecting", Toast.LENGTH_SHORT).show();
                            break;
                    }
                    break;
                case Constants.MESSAGE_WRITE:

                    /* Not currently sending anything to BT */
                    break;
                case Constants.MESSAGE_READ:
                    String[] prm = (String[])msg.obj;

                    switch(prm[0]) {
                        case "us000":
                            _pkSensor1 = Float.parseFloat(prm[1]);
                            pkSensor1.setProgress((int)(_pkSensor1 * 100));
                            txtSensor1.setText(GetValue(_pkSensor1));
                            break;
                        case "us001":
                            _pkSensor2 = Float.parseFloat(prm[1]);
                            pkSensor2.setProgress((int)(_pkSensor2 * 100));
                            txtSensor2.setText(GetValue(_pkSensor2));
                            break;
                        case "us002":
                            _pkSensor3 = Float.parseFloat(prm[1]);
                            pkSensor3.setProgress((int)(_pkSensor3 * 100));
                            txtSensor3.setText(GetValue(_pkSensor3));
                            break;
                        case "us003":
                            _pkSensor4 = Float.parseFloat(prm[1]);
                            pkSensor4.setProgress((int)(_pkSensor4 * 100));
                            txtSensor4.setText(GetValue(_pkSensor4));
                            break;
                        case "us004":
                            _pkSensor5 = Float.parseFloat(prm[1]);
                            pkSensor5.setProgress((int)(_pkSensor5 * 100));
                            txtSensor5.setText(GetValue(_pkSensor5));
                            break;
                        case "us005":
                            _pkSensor6 = Float.parseFloat(prm[1]);
                            pkSensor6.setProgress((int)(_pkSensor6 * 100));
                            txtSensor6.setText(GetValue(_pkSensor6));
                            break;
                        case "us006":
                            _pkSensor7 = Float.parseFloat(prm[1]);
                            pkSensor7.setProgress((int)(_pkSensor7 * 100));
                            txtSensor7.setText(GetValue(_pkSensor7));
                            break;
                        case "us007": /* Driver front */
                            _pkSensor8 =Float.parseFloat(prm[1]);
                            pkSensor8.setProgress((int)(_pkSensor8 * 100));
                            txtSensor8.setText(GetValue(_pkSensor8));

                            break;
                        case "lidar001":
                            txtLidar.setText(prm[1] + " - " + prm[2]);
                            _lidarDistance = Float.parseFloat(prm[1]);
                            _lidarSignalStrength = Float.parseFloat(prm[2]);

                            Log.d(TAG, String.format("Lidar %f", _lidarDistance ));

                            break;
                    }

                    break;

                case Constants.MESSAGE_SNACKBAR:


                    break;
            }
        }
    }

    private String GetValue(float value) {
        if(value == 99){
            return "out of range";
        }

        float imperial = value * 3.2808399f;
        int feet = (int)Math.floor(imperial);
        int inches = (int) ((imperial * 12) % 12.0);

        return String.format("%dft %din", feet, inches);
    }

    private final BroadcastReceiver mReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            String action = intent.getAction();
            // When discovery finds a device
            if (BluetoothDevice.ACTION_FOUND.equals(action)) {
                // Get the BluetoothDevice object from the Intent
                BluetoothDevice device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE);
                device.fetchUuidsWithSdp();

                Log.d(FullscreenActivity.TAG, String.format("Found device %s", device.getName()));

                if(device.getName() != null) {
                    Log.d(TAG, "Found device " + device.getName().toLowerCase());
                }
                else {
                    Log.d(TAG, "Found null name device ");
                }

                if(device.getName() != null &&
                        device.getName().toLowerCase().startsWith("iot truck") &&
                        mBluetoothService == null) {

                    bluetoothDevicesAdapter.add(device);
                    bluetoothDevicesAdapter.notifyDataSetChanged();

                    Log.d(FullscreenActivity.TAG, String.format("Found device %s", device.getName()));
                }
            } else if (BluetoothAdapter.ACTION_DISCOVERY_FINISHED.equals(action)) {
                Log.d(FullscreenActivity.TAG, "Finished searching");
                if(mSearchNow != null) {
                    mSearchNow.setEnabled(true);
                }
                Toast.makeText(FullscreenActivity.this, "Finished searching", Toast.LENGTH_SHORT).show();
            } else if (action.equals(BluetoothAdapter.ACTION_STATE_CHANGED)) {
                int state = intent.getIntExtra(BluetoothAdapter.EXTRA_STATE, BluetoothAdapter.ERROR);
                switch (state) {
                    case BluetoothAdapter.STATE_OFF:
                        Toast.makeText(FullscreenActivity.this, "Bluetooth turned off", Toast.LENGTH_SHORT).show();
                        break;
                }
            }
        }
    };


    @Override
    public boolean onPrepareOptionsMenu (Menu menu) {
        return true;
    }
}
