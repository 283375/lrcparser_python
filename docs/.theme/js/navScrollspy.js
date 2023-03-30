function startScrollspy() {
  const id_tocLinkEl_map = new Map()
  const targetEl_id_map = new Map()

  // build maps
  const tocLinks = Array.from(document.querySelectorAll('.toc-link'))
  tocLinks.forEach((el) => id_tocLinkEl_map.set(new URL(el.href).hash, el))

  Array.from(id_tocLinkEl_map.keys()).forEach((key) =>
    targetEl_id_map.set(document.querySelector(key), key)
  )

  // WIP: achieve something like bootstrap scrollspy
}
