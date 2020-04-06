
var exec = require('child_process').execFile;
const CronJob = require('cron').CronJob;

console.log('Before job instantiation');
const job = new CronJob('0 */10 * * * *', function() {
	   exec('crontab.sh', function(err, data) {  
        console.log(err)
        console.log(data.toString());                       
    });  
});
console.log('After job instantiation');
job.start();