var r
if(window.location.toString().match(/android/)){
  //r = new RestClient('http://10.0.2.2:8080', {contentType: 'json'});
  r = new RestClient('http://t3u-ajor.rhcloud.com', {contentType: 'json'});
}
else{
  r = new RestClient('http://127.0.0.1:8080', {contentType: 'json'});
  //r = new RestClient('http://t3u-ajor.rhcloud.com', {contentType: 'json'});
}

var cl = console.log
var finita = true

r.res('tabuloj')
r.res('rekomenci')
r.res('tabulo')
r.res('agi')
r.res('rezigni')
r.res('nuligi')
r.res('rango')

var T = document.getElementsByClassName('T')
var informoj = document.getElementById('informoj')
var informoj_uzantoO = document.getElementById('informoj_uzantoO')
var venkulo = document.getElementById('venkulo')
var informoj_uzantoX = document.getElementById('informoj_uzantoX')
var tu = document.getElementById('tu')
var rekomencu = document.getElementById('rekomencu')
var rezignu = document.getElementById('rezignu')
var nuligu = document.getElementById('nuligu')

venkulo.innerHTML = 'لطفاً صبر کنید…'

rezignu.style.display = 'none'
rekomencu.style.display = 'none'
nuligu.style.display = 'none'

if(window.localStorage.getItem("seanco") == undefined){
  window.location = 'ensaluti.html'
}

function persa(cifero){
  return cifero.replace(/0/g, "۰").replace(/1/g, "۱").replace(/2/g, "۲").replace(/3/g, "۳").replace(/4/g, "۴").replace(/5/g, "۵").replace(/6/g, "۶").replace(/7/g, "۷").replace(/8/g, "۸").replace(/9/g, "۹")
}
function prompti(msg){
  var prompto = document.getElementById('prompto')
  prompto.innerHTML = msg
  prompto.style.display = 'initial'
  prompto.className = 'montri'
}
function kasxi_prompton(){
  var prompto = document.getElementById('prompto')
  prompto.className = 'kasxi'
  setTimeout( function(){prompto.style.display = 'none'}, 1000 );
}
function montri_rangon(){
  r.rango(window.localStorage.getItem('seanco')).get().then(function(k){
    var rangoj = '<table><tr id="kapo"><td>رتبه</td><td>بازیکن</td><td>امتیاز</td>'
    for (i=0;i<7;i++){
      try{
        rangoj += '<tr><td>'+persa((i+1).toString())+'</td><td>'+k['sep_unuaj'][i.toString()][0]+'</td><td>'+persa(k['sep_unuaj'][i.toString()][1])+'</td></tr>'
      }
      catch(e){}
    }
    if(k['uzanto_rango'] > 7){
      rangoj += '<tr><td>...</td><td>...</td><td>...</td></tr>'
      rangoj += '<tr><td>'+persa(k['uzanto_rango'].toString())+'</td><td>'+k['uzanto']+'</td><td>'+persa(k['uzanto_poento'].toString())+'</td></tr>'
    }
    prompti(rangoj+'</table><div id="fermu" onclick="kasxi_prompton()">بستن</div>')
  })
}
function montri_helpanton(){
  prompti('<iframe src="i.html"></iframe>'
          + '<div id="fermu" onclick="kasxi_prompton()">بستن</div>')
}
function MSS(s){return(s-(s%=60))/60+(9<s?':':':0')+s}
function tempili(k){
  if(k['vico'] == k['uzantoO']){
    k['tempilo_uzantoO']+=1
    informoj_uzantoO.innerHTML = persa(MSS((k['fintempo']-k['tempilo_uzantoO'])).toString())+'<br>'+k['uzantoO']+'<br>امتیاز: '+persa(k['poentoO'].toString())
  }
  else if(k['vico'] == k['uzantoX']){
    k['tempilo_uzantoX']+=1
    informoj_uzantoX.innerHTML = persa(MSS((k['fintempo']-k['tempilo_uzantoX'])).toString())+'<br>'+k['uzantoX']+'<br>امتیاز: '+persa(k['poentoX'].toString())
  }
}
function preni_tabulojn(){
  var prenita = false
  r.tabuloj(window.localStorage.getItem('seanco')).get().then(function(k){
    if(k == 'ensalutu'){
      window.location = 'ensaluti.html'     
    }
    else if(!!k){
      //uzanto havas almenaux unu tabulon:
      var tuo = ''
      for(var t in k){
        if(k[t]['venkulo'] == 'naturo'){
          k[t]['venkulo'] = 'هیچ‌کس!'
        }
        if(k[t]['uzantoX'] == 'naturo'){
          k[t]['uzantoX'] = 'هیچ‌کس!'
        }
        if(k[t]['vico'] == 'naturo'){
          k[t]['vico'] = 'هیچ‌کس!'
        }
        tuo += '<option value="'+t+'" >'+persa(t)+' > '+k[t]['uzantoO'] + ' علیه ' + k[t]['uzantoX']+' | نوبت: '+k[t]['vico']+' | پیروز: '+k[t]['venkulo']+'</option>'
      }
      tu.innerHTML = tuo
      var oj = document.getElementsByTagName('option')
      if(!(window.localStorage.getItem('elektita') in k) || window.localStorage.getItem('elektita') == 'undefined'){
        window.localStorage.setItem('elektita', oj[0].value)
      }
      tu.value = window.localStorage.getItem('elektita')
      finita = false
      prenita = true
    }
    else{
      //uzanto ne havas tabulon:
      finita = true
      rezignu.style.display = 'none'
      rekomencu.style.display = ''
      nuligu.style.display = 'none'
      venkulo.innerHTML = 'یک بازی جدید شروع کنید.'
      informoj_uzantoO.innerHTML = ''
      informoj_uzantoX.innerHTML = ''
      informoj_uzantoO.className = ''
      informoj_uzantoX.className = ''
      prenita = false
    }
  })
  return prenita
}
r.tabuloj(window.localStorage.getItem('seanco')).get().then(function(k){
  preni_tabulojn()
  if(!finita){
    r.tabulo(window.localStorage.getItem('seanco')+'/'+tu.value).get().then(function(k){
      if(!k){
        rezignu.style.display = 'none'
        rekomencu.style.display = ''
        nuligu.style.display = 'none'
      }
      else{
        rezignu.style.display = ''
        rekomencu.style.display = 'none'
        nuligu.style.display = 'none'
        mapi(k)
      }
    })
  }
  setInterval(function(){
    if(!finita){
      r.tabulo(window.localStorage.getItem('seanco')+'/'+tu.value).get().then(function(k){
        if(!k){
          rezignu.style.display = 'none'
          rekomencu.style.display = ''
          nuligu.style.display = 'none'
        }
        else{
          rezignu.style.display = ''
          rekomencu.style.display = 'none'
          if(k['oponanto'] == 'naturo'){
            nuligu.style.display = ''
          }
          else{
            nuligu.style.display = 'none'
          }
          mapi(k)
        }
      })
    }
  },3000)
})
tu.addEventListener('change', function(){
  window.localStorage.setItem('elektita', tu.value)
})
function agi(I, i){
  if(!finita){
    r.agi(window.localStorage.getItem('seanco')+'/'+tu.value+'/'+I.toString()+'/'+i.toString()).get().then(function(k){
      if (typeof(k) == 'string'){
        alert(k)
      }
      else{
        mapi(k)
       }
    })
  }
}
function ijIndekso(i, j){
  return i+3*j
}
function mapi(k){
  preni_tabulojn()
  var mapo = k['Tabulo']
  var uzanto = k['uzanto']
  var vico = k['vico']
  var lastaIndekso = k['lastaIndekso']
  //reagordi Tabulojn:
  for(i=0;i<T.length;i++){
    T[i.toString()].className = 'T'
  }
  if(k['uzantoX'] == 'naturo'){
    venkulo.innerHTML = 'در انتظار یک بازیکن دیگر…<br>امتیاز شما: '+persa(k['poentoO'].toString())
    informoj_uzantoO.innerHTML = ''
    informoj_uzantoX.innerHTML = ''
    informoj_uzantoO.className = ''
    informoj_uzantoX.className = ''
    rezignu.style.display = 'none'
    rekomencu.style.display = 'none'
    nuligu.style.display = ''
  }
  else if(k['egalita']){
    finita = true
    rezignu.style.display = 'none'
    rekomencu.style.display = ''
    nuligu.style.display = 'none'
    informoj_uzantoO.innerHTML = persa(MSS((k['fintempo']-k['tempilo_uzantoO'])).toString())+'<br>'+k['uzantoO']+'<br>امتیاز: '+persa(k['poentoO'].toString())
    informoj_uzantoX.innerHTML = persa(MSS((k['fintempo']-k['tempilo_uzantoX'])).toString())+'<br>'+k['uzantoX']+'<br>امتیاز: '+persa(k['poentoX'].toString())
    informoj_uzantoO.className = ''
    informoj_uzantoX.className = ''
    venkulo.innerHTML = 'مساوی!<br>امتیاز شما: '+persa(k['poentoO'].toString())
  }
  else{
    if(k['venkulo'] != 'naturo'){
      finita = true
      rezignu.style.display = 'none'
      rekomencu.style.display = ''
      nuligu.style.display = 'none'
      informoj_uzantoO.innerHTML = persa(MSS((k['fintempo']-k['tempilo_uzantoO'])).toString())+'<br>'+k['uzantoO']+'<br>امتیاز: '+persa(k['poentoO'].toString())
      informoj_uzantoX.innerHTML = persa(MSS((k['fintempo']-k['tempilo_uzantoX'])).toString())+'<br>'+k['uzantoX']+'<br>امتیاز: '+persa(k['poentoX'].toString())
      informoj_uzantoO.className = ''
      informoj_uzantoX.className = ''
      if(k['uzanto'] == k['uzantoO']){
        venkulo.innerHTML = 'پیروز: '+k['venkulo'].toString()+'<br>امتیاز شما: '+persa(k['poentoO'].toString())
      }
      else if(k['uzanto'] == k['uzantoX']){
        venkulo.innerHTML = 'پیروز: '+k['venkulo'].toString()+'<br>امتیاز شما: '+persa(k['poentoX'].toString())
      }
    }
    else if(k['venkulo'] == 'naturo'){
      var n = 0
      function voki_tempiladon(){
        if (n < 3){
          tempili(k)
          n++
        }
        else{
          clearInterval(t)
        }
      }
      var t = setInterval(voki_tempiladon,1000)
      venkulo.innerHTML = ''
      rezignu.style.display = ''
      rekomencu.style.display = 'none'
      if(k['oponanto'] == 'naturo'){
        nuligu.style.display = ''
      }
      else{
        nuligu.style.display = 'none'
      }
      informoj_uzantoO.innerHTML = persa(MSS((k['fintempo']-k['tempilo_uzantoO'])).toString())+'<br>'+k['uzantoO']+'<br>امتیاز: '+persa(k['poentoO'].toString())
      informoj_uzantoX.innerHTML = persa(MSS((k['fintempo']-k['tempilo_uzantoX'])).toString())+'<br>'+k['uzantoX']+'<br>امتیاز: '+persa(k['poentoX'].toString())
      if(k['vico'] == k['uzantoO']){
        informoj_uzantoO.className = 'blinki'
        informoj_uzantoX.className = ''
      }
      //else:
      else if(k['vico'] == k['uzantoX']){
        informoj_uzantoO.className = ''
        informoj_uzantoX.className = 'blinki'
      }
    }
  }
  var t = ''
  for (I=0;I<=8;I++){
    t=''
    for (j=0;j<=2;j++){
      t += '<tr>'
      for (i=0;i<=2;i++){
        if(mapo[I.toString()]['S'] == 'O'){
          T[I.toString()].className = ' T O'
        }
        else if(mapo[I.toString()]['S'] == 'X'){
          T[I.toString()].className = ' T X'
        }
        t+='<td'+' id="'+i.toString()+'_'+j.toString()+'" class="'+mapo[I.toString()]['t'][ijIndekso(i, j)]+'" onclick=agi('+I.toString()+','+ijIndekso(i, j)+') ></td>'
      }
      t += '</tr>'
    }
    T[I.toString()].innerHTML = t
  }
  if(lastaIndekso == -1 && vico == uzanto){
    for(I=0;I<T.length;I++){
      if(mapo[I.toString()]['S'] == 'E'){
        T[I.toString()].className += ' aktiva'
      }
    }
  }
  else if(lastaIndekso == -1){
    for(I=0;I<T.length;I++){
      if(mapo[I.toString()]['S'] == 'E'){
        T[I.toString()].className += ' aktiva_por_aliulo'
      }
    }
  }
  else if((vico == uzanto) && (mapo[lastaIndekso.toString()]['S'] == 'E')){
    T[lastaIndekso.toString()].className += ' aktiva'
  }
  else if((vico != uzanto) && (mapo[lastaIndekso.toString()]['S'] == 'E')){
    T[lastaIndekso.toString()].className += ' aktiva_por_aliulo'
  }
  if((k['venkulo'] != 'naturo') || mapo['egalita']){
    for(i=0;i<T.length;i++){
      T[i.toString()].className = T[i.toString()].className.replace('aktiva','').replace('aktiva_por_aliulo','')
    }
  }
}

function rezigni(){
  r.rezigni(window.localStorage.getItem('seanco')+'/'+tu.value).get().then(function(k){
    window.localStorage.setItem('elektita', tu.value)
    for(i=0;i<T.length;i++){
      T[i.toString()].className = T[i.toString()].className.replace('aktiva','').replace('aktiva_por_aliulo','')
    }
  })
}

function rekomenci(){
  r.rekomenci(window.localStorage.getItem('seanco')).get().then(function(k){
    if(k['stato']){
      finita = false
      preni_tabulojn()
      venkulo.innerHTML = 'در انتظار یک بازیکن دیگر…'
      informoj_uzantoO.innerHTML = ''
      informoj_uzantoX.innerHTML = ''
      informoj_uzantoO.className = ''
      informoj_uzantoX.className = ''
      rezignu.style.display = 'none'
      rekomencu.style.display = 'none'
      nuligu.style.display = ''
      window.localStorage.setItem('elektita', k['id'])
    }
  })
}

function nuligi(){
  r.nuligi(window.localStorage.getItem('seanco')+'/'+tu.value).get().then(function(k){
    if(preni_tabulojn()){
      var oj = document.getElementsByTagName('option')
      window.localStorage.setItem('elektita', oj[0].value)
      for(i=0;i<T.length;i++){
        T[i.toString()].className = T[i.toString()].className.replace('aktiva','').replace('aktiva_por_aliulo','')
      }
    }
    finita = false
  })
}