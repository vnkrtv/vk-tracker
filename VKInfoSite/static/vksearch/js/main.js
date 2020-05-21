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

function addFilter1Page() {
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

function getInputDiv(i, label, name) {
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

function getUniversitySelect(i) {
    const container = document.createElement('div');
    container.className = 'col-md-4 mb-3';

    const select = document.createElement('select');
    select.className = 'form-control';
    select.name = `university_${i}`;
    select.id = `university_${i}`;

    for (let i = 0; i < all_universities_count; ++i) {
        const option = document.createElement('option');
        option.value = `${universities[i].id}`;
        option.innerHTML = `${universities[i].title}`;
        select.appendChild(option);
    }
    container.appendChild(select);

    return container;
}

function AddFilter2Page() {
    const universities = JSON.parse('{{ universities }}'.replace(/&#39;/gi, '"'));
    const all_universities_count = parseInt('{{ universities|length }}');
    const universities_container = document.getElementById("universities_container");

    const universities_num = document.getElementById("universities_num");
    universities_num.onkeyup = universities_num.onchange = () =>  {
        universities_container.innerHTML = universities_num.value != 0 ? 'Select univercities:': '';
        for (let i = 0; i < universities_num.value; ++i) {
            universities_container.appendChild(getUniversitySelect(i))
        }
    };

    const friends = document.getElementById('friends');
    const friends_num = document.getElementById('friends_num');
    friends_num.onkeyup = friends_num.onchange = () => {
        friends.innerHTML = friends_num.value != 0 ? 'Enter friends domains:': '';
        for (let i = 0; i < friends_num.value; ++i) {
            friends.appendChild(getInputDiv(i, 'Domain', 'friend'))
        };
    };

    const groups = document.getElementById('groups');
    const groups_num = document.getElementById('groups_num');
    groups_num.onkeyup = groups_num.onchange = () => {
        groups.innerHTML = groups_num.value != 0 ? 'Enter groups screen names:': '';
        for (let i = 0; i < groups_num.value; ++i) {
            groups.appendChild(getInputDiv(i, 'Screen name', 'group'))
        };
    };
}
