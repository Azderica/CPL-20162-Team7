package com.example.viewerproject;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Context;
import android.content.Intent;
import android.graphics.BitmapFactory;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;
import android.os.IBinder;
import android.os.Vibrator;
import android.support.v4.app.NotificationCompat;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.IOException;
import java.util.ArrayList;

import retrofit2.Call;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

public class MyService extends Service {
   ArrayList< ArrayList<ResultData> > items = new ArrayList<>();
    public static int run = 0;
    Retrofit retrofit;
    int num = 0;
    MyGlobals.RetrofitExService retrofitExService;
    Mythread t1;
    private Vibrator vibrator;
    public int flag = 0;
    public Gson gson;

    public MyService() {
    }

    @Override
    public IBinder onBind(Intent intent) {
        throw new UnsupportedOperationException("Not yet implemented");
    }

    @Override
    public void onCreate() {
        super.onCreate();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        vibrator = (Vibrator)getSystemService(Context.VIBRATOR_SERVICE);
        super.onStartCommand(intent, flags, startId);
        String Channel_id = "channel_1";
        if(Build.VERSION.SDK_INT >= 26) {
            NotificationChannel channel = new NotificationChannel(Channel_id, "Android test", NotificationManager.IMPORTANCE_LOW);
            ((NotificationManager)getSystemService(Context.NOTIFICATION_SERVICE)).createNotificationChannel(channel);
        }
        startForeground(1,new Notification());
       // String command = intent.getStringExtra("command");
        //System.out.println("command : " + command);
        t1 = new Mythread();
        t1.start();
        return START_REDELIVER_INTENT;
        //return super.onStartCommand(intent, flags, startId);
    }

    @Override
    public void onDestroy() {
        super.onDestroy();
        System.out.println("서비스 destroy");
        if(run == 1) {
            t1 = null;
            System.out.println("stop 전");
            System.out.println("stop 후");
            run = 0;
        }
    }


    class Mythread extends Thread{
        public void run(){
            run = 1;
            gson = new GsonBuilder().setLenient().create();
            System.out.println("Mythread 실행");
            while (true) {
                System.out.println("while문");
                if(run == 0) {
                    System.out.println("if run");
                    break;
                }
                System.out.println("while문 안");
                if (MyGlobals.getInstance().getRetrofit() == null || MyGlobals.getInstance().getRetrofitExService() == null) {
                    retrofit = new Retrofit.Builder().baseUrl(MyGlobals.RetrofitExService.URL).addConverterFactory(GsonConverterFactory.create(gson)).build();
                    retrofitExService = retrofit.create(MyGlobals.RetrofitExService.class);
                    MyGlobals.getInstance().setRetrofit(retrofit);
                    MyGlobals.getInstance().setRetrofitExService(retrofitExService);
                } else {
                    retrofit = MyGlobals.getInstance().getRetrofit();
                    retrofitExService = MyGlobals.getInstance().getRetrofitExService();
                }

                Call<ResultData> c = retrofitExService.getData();

                try{
                    ResultData data  = c.execute().body();
                   /* for(int i =0;i<data.size();i++){
                        System.out.println("label : "+data.get(i).getLabel() + " confidence : "+data.get(i).getConfidence() + " topleft : "+data.get(i).getTopleft() + " bottomright : "+ data.get(i).getBottomright());
                    }

                   items.add(data);
                    for(int i = 0;i<items.size();i++){
                        ArrayList<ResultData> result = items.get(i);
                       for(int j =0;j<result.size();j++){
                           if(result.get(i).equals("person")){
                               flag = 1;
                               break;
                           }
                       }
                       if(flag == 1)
                           break;
                    }

                    if(items.size() == 11){
                        items.remove(0);
                    }*/

                    try{
                        Thread.sleep(8000);
                    }catch (Exception e){
                        e.printStackTrace();
                    }

                    Uri alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
                        //System.out.println("label : " + data.getLabel() + " confidence : " + data.getConfidence() + " topleft : " + data.getTopleft() + " bottomright : " + data.getBottomright());
                        String channelId = "channel";
                        String channelName = "channel name";
                        int importance = NotificationManager.IMPORTANCE_LOW;
                        NotificationManager notiManager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);

                        if (Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) { //오레오 버전이후에는 추가해주어야한다.
                            NotificationChannel mChannel = new NotificationChannel(channelId, channelName, importance);
                            notiManager.createNotificationChannel(mChannel);
                        }
                        NotificationCompat.Builder builder = new NotificationCompat.Builder(getApplicationContext(), channelId);
                        Intent intent = new Intent(getApplicationContext(), MainActivity.class);
                        intent.setFlags(Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
                        int requestID = (int) System.currentTimeMillis();
                        PendingIntent pendingIntent = PendingIntent.getActivity(getApplicationContext(), requestID, intent, PendingIntent.FLAG_UPDATE_CURRENT);

                        builder.setLargeIcon(BitmapFactory.decodeResource(getResources(), android.R.drawable.star_on));
                        builder.setSmallIcon(android.R.drawable.star_on);
                        builder.setTicker("알람 간단 설명");
                        builder.setContentTitle("변경사항");
                        builder.setContentText("사람이 포착 되었습니다");
                        builder.setWhen(System.currentTimeMillis());
                        builder.setDefaults(Notification.DEFAULT_SOUND | Notification.DEFAULT_VIBRATE);
                        builder.setContentIntent(pendingIntent);
                        builder.setAutoCancel(true);
                        builder.setNumber(999);
                        builder.setSound(alarmSound);
                        notiManager.notify(num, builder.build());
                        vibrator.vibrate(1000);
                        num++;
                        flag = 0;

                }catch(IOException e){
                    e.printStackTrace();
                }

                try{
                    Thread.sleep(10000);
                }catch (Exception e){
                    e.printStackTrace();
                }

            }
            System.out.println("쓰레드 종료");
        }
    }
}

