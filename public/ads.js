// ===== অ্যাড কোড বসানোর ফাইল =====
// amanahads.com (বা অন্য নেটওয়ার্ক) থেকে পাওয়া অ্যাড কোড নিচের ব্যাকটিকের (`) ভেতরে পেস্ট করুন।
// এক জায়গায় বদলালে সব পেজে বদলে যাবে। ফাঁকা থাকলে কোনো অ্যাড দেখাবে না।
var AD_TOP = ``;
var AD_BOTTOM = ``;

function putAd(id, code) {
  var el = document.getElementById(id);
  if (!el || !code.trim()) return;
  el.innerHTML = code;
  // innerHTML দিয়ে বসালে <script> চলে না, তাই নতুন করে বানিয়ে বসাই
  el.querySelectorAll("script").forEach(function (old) {
    var s = document.createElement("script");
    for (var i = 0; i < old.attributes.length; i++) {
      s.setAttribute(old.attributes[i].name, old.attributes[i].value);
    }
    s.text = old.text;
    old.parentNode.replaceChild(s, old);
  });
}
putAd("ad-top", AD_TOP);
putAd("ad-bottom", AD_BOTTOM);
