-- wait_time = 1
-- patient_time = 10

-- function wait_for(splash, selector)
--     local total_wait = 0
--     while not splash:select(selector) do
--         splash:wait(wait_time)
--         total_wait = total_wait + wait_time
--         if total_wait > patient_time then
--             break
--         end
--     end
-- end

-- function main(splash, args)
--     assert(splash:go(args.url))
--     wait_for(splash, 'footer')
--     splash:set_viewport_full()
--     -- splash:runjs()
--     return splash:html()
-- end

wait_time = 1
patient_time = 10

function wait_for(splash, selector)
    local total_wait = 0
    while not splash:select(selector) do
        splash:wait(wait_time)
        total_wait = total_wait + wait_time
        if total_wait > patient_time then
            break
        end
    end
end

function main(splash, args)
    assert(splash:go(args.url))
    wait_for(splash, 'footer')

    local link = splash:select('.board-nav-page.last')
    local last_page_number = link:text()

    splash:set_viewport_full()
    splash:runjs()
    return {last_page_number=last_page_number, html=splash:html()}
end

