# to run 
# scrapy crawl TMDB_spider -o movies.csv

import scrapy

class TMDB_Spider(scrapy.Spider):
    name = 'TMDB_Spider'
    start_urls = ['https://www.themoviedb.org/movie/240-the-godfather-part-ii']
    
    def parse(self, response):
        """
        main parser that starts from the favourite movie page and goes to the cast page
        """
        
        #since we already know the pattern, we will just hardcode the page to the cast&crew
        cast_url = self.start_urls[0] + '/cast'
        #then we proceed to calling the parse_full_credits method with the new url
        yield scrapy.Request(url=cast_url, callback=self.parse_full_credits)
    
    def parse_full_credits(self, response):
        """
        cast&crew page parser that traverses through pages of all the cast of the movie
        """
        # the cast information is put under the ol (ordered lists) with class name "people" and "credits "
        # get characters information corresponding to each cast member from the <p> tag with class name character
        characters = response.css("ol")[0].css("p.character::text").getall()
        # the link to individual cast page is put in <a href = [relative path]>
        castlinks = response.css("ol")[0].css("div.info").css("a::attr(href)").getall()
        #use list comprehension to exclude uncredited cast members' pages
        creditedlinks = [castlinks[i] for i in range(len(castlinks)) if "(uncredited)" not in characters[i]]
        # we can hardcode the link to filter for works the person act in
        # use list comprehension to generate the list of cast pages
        creditedlinks = [i+"?credit_department=Acting" for i in creditedlinks]
        casts = [response.urljoin(link) for link in creditedlinks]
        for cast in casts:
            yield scrapy.Request(cast, callback = self.parse_actor_page)
    
    def parse_actor_page(self, response):
        """
       start on the page of actor, yield information about the actor's work
        """
        
        #get actor name: actor name is in the title of the page before the '-' dash symbol
        title = response.css("title::text").get()
        actor_name = title.split(" —")[0]

        # acting infromation is put under the first table with class 'card' and 'credits'
        # enclosed in <bdi> is the name of the work
        shows = response.css("table.credits")[0].css("bdi::text").getall()
        for work in shows:
            yield {"actor" : actor_name, "show_name" : work}

