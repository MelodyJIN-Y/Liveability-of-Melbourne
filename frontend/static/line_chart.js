let table = document.getElementById("json").innerHTML;
let labels = document.getElementById("labels").innerHTML;
let values = document.getElementById("values").innerHTML;

console.log(table);
console.log(labels);
console.log(values);

let chart = new Chart('chart1', {
type: 'bar',
data: {
  labels: ,
  datasets: [{
    label: 'My First Dataset',
    data: [1,2,3,4,5,6]
  }

]
}

});

