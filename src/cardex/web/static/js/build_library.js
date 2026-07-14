async function main() {
    // TODO something similar to build_wishlist.js where we section by set
    let card_library = document.getElementById("cards")
    let response = await fetch("/uploads")
    let library_uploads = await response.json()
    for (const upload of library_uploads) {
        let card_element = await generate_uploaded_card(upload.imgsrc, upload.upload_id)
        card_library.appendChild(card_element)
    }

    // Show the user how many cards are being processed
    window.setInterval(async function(){
        response = await fetch("/status")
        let status = await response.json()
        let cards_processing = status.cards_processing
        if (cards_processing > 0) {
            document.getElementById("upload_count").innerText = cards_processing
            document.getElementById("cards_processing_container").classList.remove("hidden")
        }
        else {
            document.getElementById("cards_processing_container").classList.add("hidden")
        }
    }, 1000);
}