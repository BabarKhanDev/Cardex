async function main() {
    console.log("test")
    let body = document.getElementById("sets")
    let response = await fetch("/all_sets")
    let set_data = await response.json();

    // When we first see a series we want to create a section for it
    // We will also loop through all sets and create icons for them
    let found_series = new Set()

    Object.entries(set_data.reverse()).forEach((entry) => {
        let series = entry[1]["series"]

        if (!(found_series.has(series))) {
            create_section(series, body)
            found_series.add(series)
        }

        let image_url = entry[1]["image_url"]
        let name = entry[1]["name"]
        let id = entry[1]["id"]

        make_set_button(image_url, name, series, id)
    });

}

function create_section(series, body) {

    let series_sets_container = document.createElement("div")
    series_sets_container.id = series + "_sets"
    series_sets_container.className = "series_container"

    let series_label = document.createElement("h2")
    series_label.innerHTML = series[0].toUpperCase() + series.slice(1).toLowerCase()
    series_label.className = "series_label"

    let series_section = document.createElement("section")
    series_section.id = series
    series_section.className = "series_section"
    series_section.append(series_label, series_sets_container)

    body.appendChild(series_section)

}

function make_set_button(image_url, name, series, id) {

    let set_element = document.createElement("img")
    set_element.alt = name + "logo"
    set_element.className = "set_image"
    set_element.src = image_url

    let set_text = document.createElement("p")
    //set_text.className = "set_text"
    //set_text.innerText = name

    let background = document.createElement("div")
    background.className = "set_background"
    background.append(set_element)

    let set_container = document.createElement("a")
    set_container.className = "set_container"
    set_container.href = "../explore/" + id
    set_container.append(background)
    //set_container.append(set_text)

    let series_container = document.getElementById(series + "_sets")
    series_container.appendChild(set_container)
}
