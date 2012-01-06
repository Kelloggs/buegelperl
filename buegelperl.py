import Image, ImageDraw
import sys, os
import random
from numpy import array, sqrt, dot, zeros

# size of your buegelperlen noppenfeld (or what ever this is called)
size = 29, 29

def main():
    for infile in sys.argv[1:]:
        outfile = os.path.splitext(infile)[0] + "_result.tiff"
        source = Image.open(infile)
        source = source.resize((size[0] * 3, size[1] * 3))
        result = k_means(source, 6)
        result = result.resize((size[0], size[1]))
        tmp = Image.new("RGB", (size[0] * 20, size[1] * 20), "#FFFFFF")

        # generate nice buegelperl output
        draw = ImageDraw.Draw(tmp)  
        pixels = result.load()
        for x in range(size[0]):
            for y in range(size[1]):
                box = (x * 20, y * 20, (x + 1) * 20, (y + 1) * 20)
                draw.ellipse(box, fill=pixels[x, y], outline=pixels[x, y])

        # save it. save it. SAVE IT!!
        tmp.save(outfile, "TIFF")


def k_means(image, k):
    # open image and initialize result image
    m = []
    result = image.copy()
    pix = image.load()
    pix_copy = result.load()    

    # initialize (randomized) means
    # TODO: need better distribution for initial means
    for value in range(k):
        while True:
            random.seed()
            randx = random.randint(0, image.size[0] - 1)
            randy = random.randint(0, image.size[1] - 1)
            # make sure, we have k different initial means and not the same one multiple times
            tmp_mean = array(pix[randx,randy])
            if not any((tmp_mean == x).all() for x in m):
                m.append(tmp_mean)
                break

    # initialize clusters (corresponding to k)
    clusters = {}
    for test in range(k):
        clusters[test] = []

    # flag to stop algorithm, if means converged
    changed = True
    iterator = 0

    while changed == True and iterator < 20:
        iterator += 1
        print "Iteration " + str(iterator)
        
        # generate clusters according to actual means
        # modify result picture 
        for x in range(image.size[0]):
            for y in range(image.size[1]):
                min_dist = None
                best_m = None
                for count in range(len(m)):
                    dist_vec = array(pix[x,y]) - m[count]         
                    dist_len = sqrt(dot(dist_vec, dist_vec))
                    if (min_dist == None) or (dist_len < min_dist):
                        min_dist = dist_len
                        best_m = count
                        
                clusters[best_m].append(pix[x,y])
                pix_copy[x,y] = tuple(m[best_m])
                
        # recalculation of means. if they were changed, the flag is set to True   
        changed = False      
        for mean in range(len(clusters)):
            cumulate = zeros(len(clusters[mean][0]))
            # sum up all values in this cluster
            for value in range(len(clusters[mean])):
                cumulate = cumulate + clusters[mean][value]

            # and normalize (and convert to int)
            m_new = cumulate/len(clusters[mean])
            m_new = m_new.astype('uint32')

            # check if the mean changed (for halting reasons)
            if not all(m_new == m[mean]):
                m[mean] = m_new
                changed = True

    return result 


if __name__ == "__main__":
    main()