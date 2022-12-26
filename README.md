
# Bridge Socket To API Service With Python Flask, ISO8583
![alt text](https://github.com/nurchulis/bridge-socket-to-api-with-iso-8583_/blob/feature/main/documentation/banner_documentation.png?raw=true)

How to handle socket connection Bridge to web service 


## Feature
- Bridge socket connection to flask webservice
- Provide NNM and (For Now will be hide Transaction Request Data)
- CRC check
- Server For Tester Demo 

## About ISO8583

 - [Belajar ISO 8583](https://rizkimufrizal.github.io/belajar-iso-8583/)
 - [Apa sih Fungsi ISO 8583?](https://dosenit.com/kuliah-it/apa-sih-fungsi-iso-8583)
 - [Source Libs](https://github.com/Seedstars/python-iso8583)
 

## Flow Apps

![alt text](https://raw.githubusercontent.com/nurchulis/bridge-socket-to-api-with-iso-8583_/feature/main/documentation/Screen%20Shot%202022-12-26%20at%2023.45.03.png)


## API Reference For Test

#### Logon 

```http
  GET api/v1/network/login
```

More comming soon
## Installation

Sorry For now just running on python 2.7

```just install python app.py
   and run server
   python test/reciever_sender.py
  
```

## Result

- Client Log
![alt text](https://raw.githubusercontent.com/nurchulis/bridge-socket-to-api-with-iso-8583_/feature/main/documentation/Client-Log.png)

- Server Log
![alt text](https://raw.githubusercontent.com/nurchulis/bridge-socket-to-api-with-iso-8583_/feature/main/documentation/Server-Log.png)


Notes Need Improvment
- Handle connection on thread looping with redis to save temporary data when request
- Provide Unitest for test case

## Tech Stack
**Code:** Python
    
