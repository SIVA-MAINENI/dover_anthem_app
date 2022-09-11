import './App.css';
import React, {  useState } from "react";

function App() {
  const [i, set_i] = useState(0);
  const [product_url, set_ads] = useState('');
  const [dummy, set_d] = useState('');
  const [car, set_car] = useState('');
  const [rewards1, set_rewards1] = useState('');
  const [rewards2, set_rewards2] = useState('');
  const [rewards3, set_rewards3] = useState('');
  const cars_urls = ["https://raw.githubusercontent.com/SIVA-MAINENI/dover_anthemnxt/master/car-photos/AudiA5.jpeg", "https://raw.githubusercontent.com/SIVA-MAINENI/dover_anthemnxt/master/car-photos/ToyotaAvalon.jpeg"];
  const kids_urls = ["https://raw.githubusercontent.com/SIVA-MAINENI/dover_anthemnxt/master/kids_photos/istockphoto-655793928-612x612.jpg", "https://raw.githubusercontent.com/SIVA-MAINENI/dover_anthemnxt/master/kids_photos/istockphoto-1135085010-612x612.jpg"];

  const requestOptions = {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ img_url1: cars_urls[i], img_url2: kids_urls[i], token: "fl80c5kmp8d6ekjz3433fgfgf", storeID: 78705, gallonCount: 5})
  };
  
  function fetchData(){
    console.log("hey")
    fetch("/personalize_ads", requestOptions)
      .then(res => res.json())
      .then((data) => {
        set_ads(data['product_url'][0]);
        set_d(data['product_url'][1]);
        set_car(data['cars_ad']);
        set_rewards1(data['product_rewards'][0]);
        set_rewards2(data['product_rewards'][1]);
        set_rewards3(data['rewardPoints']);
        console.log(data)
      })
      if(i === 0)
      {
         set_i(1);
      }
      else
      {
        set_i(0);
      }
    }

  return (
    <div className="App">
      <header className="App-header">
        <div className="flex relative">
          <h2> Your total reward points are {rewards3}</h2>
          <h6> Redeem this for just {rewards1} points</h6>
          <img
            alt="gallery"
            className="absolute inset-0 w-full h-full object-cover object-center"
            src={product_url}
          />
          <h6> Redeem this for just {rewards2} points</h6>
          <img
            alt="gallery"
            className="absolute inset-0 w-full h-full object-cover object-center"
            src={dummy}
          />
          <br/>
          <br/>
          <img
            alt="gallery"
            className="absolute inset-0 w-full h-full object-cover object-center sm:w-1/2 w-100 p-4"
            src={car}
          />
        </div>
              <button onClick={fetchData}> click me</button>
      </header>
    </div>
  );
}

export default App;
