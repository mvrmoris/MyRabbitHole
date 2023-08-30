document.addEventListener("DOMContentLoaded", () => {
  const search = document.querySelector("#search");
  if (search !== null)
  {
      search.onkeyup = () => {
          console.log(search.value); //checking for keyup events on search
          get_results(search.value);
      };
  }
});
function get_results(query)
{
    if (query === null)
    {
        return []
    }
    if (query !== "")
    {
        fetch(`/search/${query}`)
        .then(response => response.json())
        .then(result => {
            console.log(result); //works
            var x = 0;
            let table = document.getElementById('resulting');
            table.innerHTML = '';
            result.forEach(query => {
                console.log(query);
                const tr = document.createElement('tr');
                const td1 = document.createElement('td');
                const a = document.createElement('a');
                a.style.cssText = 'color:black;font-family:Quicksand;';
                let name = document.createTextNode(query.user_id)

                a.href = '/profile/'+ query.user_id;
                a.appendChild(name)
                td1.appendChild(a);
                tr.appendChild(td1);
                table.appendChild(tr);
            });
        });
    }
}




const checkbox = document.getElementById("checkbox")
checkbox.addEventListener("change", () => {
  document.body.classList.toggle("dark")
})
function toggle_visibility(el){
  var elem = document.getElementById(el);
  if (elem.style.visibility == "visible"){
    elem.style.visibility = "hidden";
  }
  else {
    elem.style.visibility = "visible";
  }
}
