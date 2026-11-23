// For tech.httptoolkit.pinning_demo v1.7.1 only, in an authorized lab.
// This suppresses the OkHttp pin check for the demo's dedicated test hostname.
Java.perform(function () {
  var Pinner = Java.use('okhttp3.CertificatePinner');
  ['check', 'check$okhttp'].forEach(function (name) {
    try {
      Pinner[name].overloads.forEach(function (overload) {
        console.log('hooking ' + name + '(' + overload.argumentTypes.map(x => x.className).join(',') + ')');
        overload.implementation = function (hostname) {
          if (hostname === 'rsa8192--untrusted-root.testserver.host') {
            console.log('bypassed OkHttp pin check for ' + hostname);
            return;
          }
          return overload.apply(this, arguments);
        };
      });
    } catch (error) {
      console.log('skip ' + name + ': ' + error);
    }
  });
});
