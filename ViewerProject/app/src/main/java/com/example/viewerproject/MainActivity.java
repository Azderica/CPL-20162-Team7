package com.example.viewerproject;

import android.content.Intent;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Spinner;
import android.widget.TextView;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.net.Socket;
import java.net.UnknownHostException;
import java.util.ArrayList;

import retrofit2.Retrofit;

public class MainActivity extends AppCompatActivity {
    private WebView webView;
    private Button on;
    private EditText editText;
    private Button left, right,up,down;
    private Spinner spinner;
    private ArrayAdapter arrayAdapter;
    public static TextView textView;
    String Uri;
    String s_ip = "220.66.219.242"; // 서버 ip
    String ip = ""; //라즈베리파이 ip
    int port =8000; // 라즈베리파이와의 통신 포트
    int s_port = 3000; // 서버와의 통신 포트

    public int flag;
    Socket c_socket = null; //라즈베리 파이와의 통신
    Socket s_socket = null; // 서버와의 통신
    Button original,black,color,yolo;
    Button start,stop;

    Retrofit retrofit ;
    MyGlobals.RetrofitExService retrofitExService;
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        textView = (TextView)findViewById(R.id.object);
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        LoginActivity.activity.finish();
        original =  (Button)findViewById(R.id.original);
        black = (Button)findViewById(R.id.black);
        color = (Button)findViewById(R.id.color);
        yolo = (Button)findViewById(R.id.yolo);
        start = (Button)findViewById(R.id.start);
        stop = (Button)findViewById(R.id.stop);
        c_socket = null;
        on = (Button) findViewById(R.id.on);
        editText = (EditText) findViewById(R.id.url);
        left = (Button) findViewById(R.id.left);
        right = (Button) findViewById(R.id.right);
        up = (Button)findViewById(R.id.up);
        down = (Button)findViewById(R.id.down);
        webView = (WebView)findViewById(R.id.webView);
        webView.setWebViewClient(new WebViewClient());



        on.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                System.out.println("on 버튼 클릭");
                webView.setInitialScale(100);
                webView.loadUrl(editText.getText().toString());
                webView.getSettings().setJavaScriptEnabled(true);
                webView.getSettings().setAppCacheMaxSize( 10 * 1024 * 1024 ); // 10MB
                webView.getSettings().setAppCachePath(getApplicationContext().getCacheDir().getAbsolutePath() );
                webView.getSettings().setAllowFileAccess( true );
                webView.getSettings().setAppCacheEnabled( true );
                webView.getSettings().setJavaScriptEnabled( true );
                webView.getSettings().setCacheMode( WebSettings.LOAD_DEFAULT );
                webView.getSettings().setLoadWithOverviewMode(true);
                webView.getSettings().setUseWideViewPort(true);
                webView.setScrollBarStyle(WebView.SCROLLBARS_OUTSIDE_OVERLAY);
                webView.setScrollbarFadingEnabled(true);
            }
        });

        start.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                //서비스 실행
                System.out.println("버튼클릭 서비스시작");
                Intent intent = new Intent(getApplicationContext(),MyService.class);
                intent.putExtra("command","show");
                startService(intent);
            }
        });

        stop.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                Intent intent = new Intent(getApplicationContext(),MyService.class);
                stopService(intent);
            }
        });

        left.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                flag = 0;
                new MyClient().execute(); //라즈베리파이로 데이터전송
            }
        });

        right.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                flag = 1;
                new MyClient().execute(); //라즈베리파이로 데이터전송
            }
        });

        up.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                flag = 2;
                Intent intent = new Intent(getApplicationContext(), LoginActivity.class);
                startActivity(intent);
               // new MyClient().execute();
            }
        });

        down.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                flag = 3;
                new MyClient().execute();
            }
        });

        /* Myeonghun edit */
        ArrayList Spinner_arrayList = new ArrayList<>();
        Spinner_arrayList.add("Camera 1");
        Spinner_arrayList.add("Camera 2");
        Spinner_arrayList.add("Camera 3");
        Spinner_arrayList.add("Camera 4");
        Spinner_arrayList.add("Camera 5");
        Spinner_arrayList.add("Camera 6");

        spinner = (Spinner)findViewById(R.id.spinner2);

        arrayAdapter = new ArrayAdapter<>(getApplicationContext(),android.R.layout.simple_spinner_dropdown_item,Spinner_arrayList);

        spinner.setAdapter(arrayAdapter);


    }

    public void onClick(View v){
        switch(v.getId()){
            case R.id.original:
                editText.setText("http://20.20.0.82:5000/video_feed_original");
                break;
            case R.id.black:
                editText.setText("http://20.20.0.82:5000/video_feed_grayscale");
                break;
            case R.id.color:
                editText.setText("http://20.20.0.82:5000/video_feed_colorized");
                break;
            case R.id.yolo:
                editText.setText("http://20.20.0.82:5000/video_feed_yolo");
                break;
        }

        System.out.println("on 버튼 클릭");
        webView.setInitialScale(100);
        webView.loadUrl(editText.getText().toString());
        webView.getSettings().setJavaScriptEnabled(true);
        webView.getSettings().setAppCacheMaxSize( 10 * 1024 * 1024 ); // 10MB
        webView.getSettings().setAppCachePath(getApplicationContext().getCacheDir().getAbsolutePath() );
        webView.getSettings().setAllowFileAccess( true );
        webView.getSettings().setAppCacheEnabled( true );
        webView.getSettings().setJavaScriptEnabled( true );
        webView.getSettings().setCacheMode( WebSettings.LOAD_DEFAULT );
        webView.getSettings().setLoadWithOverviewMode(true);
        webView.getSettings().setUseWideViewPort(true);
        webView.setScrollBarStyle(WebView.SCROLLBARS_OUTSIDE_OVERLAY);
        webView.setScrollbarFadingEnabled(true);
    }


   class S_Thread extends Thread{
       public void run(){
           if(s_socket==null) {
               try {
                   System.out.println("S_thread 실행");
                   s_socket = new Socket(s_ip,s_port);
                   System.out.println("s_socket :"+s_socket);
                   System.out.println("server socket 생성됨");
                   BufferedWriter writer = new BufferedWriter(new OutputStreamWriter(s_socket.getOutputStream()));
                   String s = "start";
                   writer.write(s);
                   writer.flush();
                   System.out.println("server로의 전송 완료");

                   while(true){
                       //서버로부터 데이터를 받음
                       InputStream input = s_socket.getInputStream();
                       DataInputStream dis = new DataInputStream(input);
                       BufferedReader reader = new BufferedReader(new InputStreamReader(input));

                       byte buf[] = new byte[16];
                        //System.out.println(dis.readInt());
                       dis.readFully(buf);
                        //String length = URLDecoder.decode(buf.toString(),"UTF-8");
                       String length =  new String(buf,"UTF-8");
                       System.out.println("length:" + length); //파일길이 UTF-8 decode
                       String real_len="";
                       for(int i =0;i<length.length();i++){
                            if(length.charAt(i)>='0' && length.charAt(i)<='9'){
                                real_len+=length.charAt(i);
                            }else {
                                break;
                            }
                       }
                       //파일 읽어오기
                       System.out.println("real_len : "+real_len);

                       /* byte buffer[] = new byte[1024];
                       int len;
                       int total_len = 0;
                       while( (len = dis.read(buffer)) != -1 ){
                           total_len +=len;
                           if(total_len>=Integer.parseInt(real_len))
                               break;
                       } //문제생김 real_len보다 더 많이받을수도있다....
                       System.out.println("String_data_length : "+total_len);
                       System.out.println("String_buffer_length : "+ buffer.length);*/

                       byte buffer[] = new byte[Integer.parseInt(real_len)];
                       dis.readFully(buffer);
                       String buffer_str = new String(buffer,"UTF-8");
                       buffer = buffer_str.getBytes();
                       //System.out.println("String_data : "+buffer);
                       System.out.println("buffer_len : " + buffer.length);
                       System.out.println("buffer_str len : "+buffer_str.length());

                       /*File file = new File(Environment.getExternalStorageDirectory()+"/"+"test");
                       FileOutputStream out = new FileOutputStream(file);
                       DataOutputStream dout = new DataOutputStream(out);
                       dout.write(buffer,0,Integer.parseInt(real_len)); //파일에 쓰기
                       runOnUiThread(new Runnable() {
                           @Override
                           public void run() {
                                 //이미지뷰에 파일 넣기
                               android.net.Uri uri = android.net.Uri.parse("file:///" + Environment.getExternalStorageDirectory()+"/"+"test");
                               imageView.setImageURI(uri);
                           }
                       });*/
                   }

               }catch(IOException e){
                   e.printStackTrace();
               }
           }
       }
   }

    public class MyClient extends AsyncTask<Void, Void, Void> {
        @Override
        protected void onPostExecute(Void aVoid) {
            super.onPostExecute(aVoid);
        }

        @Override
        protected Void doInBackground(Void... voids) {
            System.out.println("socket : "+c_socket);
            try{
                if(c_socket == null) {
                    System.out.println("socket 생성전@@@@@@@@@@@@@@@@@@@@");
                    c_socket = new Socket(ip, port);
                    System.out.println("socket 생성됨@@@@@@@@@@@@@@@@" + c_socket);
                }
                //송신
                OutputStream output = c_socket.getOutputStream();
                String line = "null";
                if(flag ==0){
                    line = "left";
                }else if(flag == 1){
                    line = "right";
                }else if(flag == 2){
                    line = "up";
                }else if (flag == 3){
                    line = "down";
                }
                System.out.println("line : "+line);
                System.out.println("byte length : "+line.getBytes().length);
                output.write(line.getBytes());
                System.out.println("전송 ");
            }catch(UnknownHostException e){
                e.printStackTrace();
            }catch(IOException e){
                e.printStackTrace();
            }
            return null;
        }
    }
}