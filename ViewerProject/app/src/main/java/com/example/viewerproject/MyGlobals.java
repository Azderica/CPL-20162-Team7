package com.example.viewerproject;

import retrofit2.Call;
import retrofit2.Retrofit;
import retrofit2.http.GET;

public class MyGlobals {
    private Retrofit retrofit =null;
    private RetrofitExService retrofitExService = null;
    private static MyGlobals instance = null;

    public Retrofit getRetrofit() {
        return retrofit;
    }

    public void setRetrofit(Retrofit retrofit) {
        this.retrofit = retrofit;
    }

    public RetrofitExService getRetrofitExService() {
        return retrofitExService;
    }

    public void setRetrofitExService(RetrofitExService retrofitExService) {
        this.retrofitExService = retrofitExService;
    }

    public static  synchronized MyGlobals getInstance() {
        if(instance == null)
            instance = new MyGlobals();
        return instance;
    }

    public static void setInstance(MyGlobals instance) {
        MyGlobals.instance = instance;
    }

    public interface RetrofitExService{
        public static final String URL = "http://20.20.0.82:5000";

        @GET("/get/information")
        Call<ResultData> getData();

    }

}



