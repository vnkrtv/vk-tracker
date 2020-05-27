function getCity(i, label, name) {
    const container = document.createElement('div');
    container.className = "col-md-4 mb-3";

    const option_label = document.createElement('label');
    option_label.htmlFor = `${name}_${i}`;
    option_label.innerHTML = `${label} ${i + 1} :`;

    const option_input = document.createElement('input');
    option_input.type = 'text';
    option_input.id = `${name}_${i}`;
    option_input.name = `${name}_${i}`;
    option_input.required = 'required';

    container.appendChild(option_label);
    container.appendChild(option_input);

    return container;
}

function main() {
    const cities = document.getElementById('cities');
    const cities_num = document.getElementById('cities_num');
    cities_num.onkeyup = cities_num.onchange = () => {
        const count = +(cities_num.value);
        cities.innerHTML = '';
        for (let i = 0; i < count; ++i) {
            cities.appendChild(getCity(i, 'City', 'city'))
        };
    };

    const un_cities = document.getElementById('un_cities');
    const un_cities_num = document.getElementById('un_cities_num');
    un_cities_num.onkeyup = un_cities_num.onchange = () => {
        const count = +(un_cities_num.value);
        un_cities.innerHTML = '';
        for (let i = 0; i < count; ++i) {
            un_cities.appendChild(getCity(i, 'University city', 'un_city'))
        };
    };
}
