var r
if(window.location.toString().match(/android/)){
  //r = new RestClient('http://10.0.2.2:8080', {contentType: 'json'});
  r = new RestClient('http://t3u-ajor.rhcloud.com', {contentType: 'json'});
}
else{
  r = new RestClient('http://127.0.0.1:8080', {contentType: 'json'});
  //r = new RestClient('http://t3u-ajor.rhcloud.com', {contentType: 'json'});
}
r.res('ensaluti')
r.res('ordo')

function ensaluti(){
  var nomo = document.getElementById("nomo").value
  var pasvorto = document.getElementById("pasvorto").value
  r.ensaluti(nomo+"/"+pasvorto).get().then(function(k){
    if(!k){
      alert("نام‌کاربری و گذرواژه مطابق نیستند!")
    }
    else if(k['seanco'] == 'undefined'){
      alert('خطای داخلی سرور :(')
    }
    else{
      window.localStorage.setItem('seanco', k['seanco'])
      window.localStorage.setItem('x', k['x'])
      window.localStorage.setItem('y', k['y'])
      window.location = 'tttu.html'
      }
  })
}
function sendi_ordojn(){
  r.ordo(window.localStorage.getItem('seanco')+'/'+window.localStorage.getItem('ordoj')).get().then(function(k){
    if(k){
      window.localStorage.setItem('ordoj', '');
      window.location.reload()
    }
  })
}