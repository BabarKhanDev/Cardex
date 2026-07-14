async function main() {
    // Get our wishlist, and display them in sections of their sets

    let card_library = document.getElementById("sets")

    // Get the wishlisted card ids
    let response_wishlist = await fetch("/wishlist_id")
    let wishlist_ids = await response_wishlist.json()
    let wishlist_cards = []

    // Get the set of each card from /card/card_id
    let wishlist_sets = new Set()
    for (const [card_id, _] of Object.entries(wishlist_ids)) {
        let response = await fetch(`/card/${card_id}`)
        let card_details = await response.json()
        wishlist_cards.push(card_details)
        wishlist_sets.add(card_details.set_id)
    }

    // Get a sorted list of all set ids that we have wishlisted
    let response_sets = await fetch("/all_sets")
    let all_sets = await response_sets.json()
    let all_set_ids = all_sets.map(obj => obj.id)
    let sorted_wishlist_sets = all_set_ids.filter(name => wishlist_sets.has(name));

    // Create a section for each set
    let id_to_name = all_sets.map(obj => [obj.id, obj.name])
    let found_series = new Set()
    sorted_wishlist_sets.forEach(set_id => {
        if (!(found_series.has(set_id))) {
            let set_name = id_to_name.filter(obj => (obj[0] === set_id))[0][1]
            create_section(set_name, set_id, card_library)
            found_series.add(set_id)
        }
    })

    // Add the cards to their relevant section
    for (const card of wishlist_cards) {
        let wanted = wishlist_ids[card.id]
        let set_id = card.set_id
        let card_element = await generate_card(card.id, card.image_url_large, card.image_url_small, wanted)
        document.getElementById(set_id + "_cards").appendChild(card_element)
    }
}

function create_section(series, set_id, body) {

    let series_cards_container = document.createElement("div")
    series_cards_container.id = set_id + "_cards"
    series_cards_container.className = "series_container"

    let series_label = document.createElement("h2")
    series_label.innerText = series.replace(/\b\w/g, char => char.toUpperCase()) // This will replace the first character of each string with a capital letter
    series_label.className = "series_label"

    let series_section = document.createElement("section")
    series_section.id = series
    series_section.className = "series_section"
    series_section.append(series_label, series_cards_container)

    body.appendChild(series_section)

}