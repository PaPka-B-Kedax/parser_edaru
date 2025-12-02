API_URL = "https://eda.rambler.ru/api/v2/graphql"

CONCURRENCY = 5

LIMIT = 14

HEADERS = {
    'Accept': 'application/json',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru,en;q=0.9',
    'Content-Type': 'application/json',
    'Cookie': 'ruid=ugsAAL+nLmkCDWY0AQ8GAAB=; eda_view=full; _ym_uid=1764665285496115862; _ym_d=1764665285; _ym_visorc=b; ruid=AAAAAMSnLmmWXGqhAdvlCwB=; _ym_isad=1; adtech_uid=bf77bbd9-ba20-4157-b729-8bf0c70e96ef%3Arambler.ru; top100_id=t1.2635991.1983173273.1764665286461; r_id_split=3; __ldr_auto_key=ed3a6c10-faeb-4f59-bcb9-ec4be6e8dcff; t3_sid_29811=s1.1153858358.1764665304679.1764665310535.1.9.1.0..; t3_sid_7726560=s1.411218198.1764665304684.1764665310536.1.7.1.0..; t3_sid_7731083=s1.1133623212.1764665305370.1764665310537.1.6.1.0..; rchainid=%7B%22message%22%3A%22need%20session%22%2C%22code%22%3A-4000%2C%22details%22%3A%7B%22method%22%3A%22%2Fsession%2FgetRsidx%22%2C%22requestId%22%3A%22ridzYaR9JpKuNvnVDe56%22%7D%7D; t3_sid_2635991=s1.1315326202.1764665286463.1764665429164.1.36.7.1..; t3_sid_7728281=s1.55843561.1764665286469.1764665429165.1.42.8.1..; CookiesAccept=accept',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 YaBrowser/25.10.0.0 Safari/537.36',
    'Origin': 'https://eda.rambler.ru',
    'Referer': 'https://eda.rambler.ru/recepty/supy'
}

QUERY_STRING = """
query recipesInfinityScrollList($offset: Int, $first: Int, $specialProjectId: ID, $sortField: RecipeSort, $similarRecipeId: ID, $recipeGroupId: ID, $recipeCategoryId: ID, $isWithVideo: Boolean, $isWithStory: Boolean, $isWithPhotoInSteps: Boolean, $isEditorChoice: Boolean, $includeIngredientIds: [ID], $excludeIngredientIds: [ID], $dietId: ID, $cuisineId: ID, $isRestaurantRecipe: Boolean, $isChefRecipe: Boolean, $cookingMethodId: ID, $artworkId: ID, $eventId: ID, $sortDirection: SortDirection) {
  recipes(
    request: {offset: $offset, first: $first, specialProjectId: $specialProjectId, sortField: $sortField, similarRecipeId: $similarRecipeId, recipeGroupId: $recipeGroupId, recipeCategoryId: $recipeCategoryId, isWithVideo: $isWithVideo, isWithStory: $isWithStory, isWithPhotoInSteps: $isWithPhotoInSteps, isEditorChoice: $isEditorChoice, includeIngredientIds: $includeIngredientIds, excludeIngredientIds: $excludeIngredientIds, dietId: $dietId, cuisineId: $cuisineId, isRestaurantRecipe: $isRestaurantRecipe, isChefRecipe: $isChefRecipe, cookingMethodId: $cookingMethodId, artworkId: $artworkId, eventId: $eventId, sortDirection: $sortDirection}
  ) {
    nodes {
      ...RecipeData
      __typename
    }
    totalCount # <-- ИЗМЕНЕНИЕ 2: totalCount ПРЯМО ЗДЕСЬ
    pageInfo {
      hasNextPage
      __typename
    }
    __typename
  }
}

fragment RecipeData on RecipeModel {
  id
  name
  relativeUrl
  portionsCount
  cookingTime
  likes
  dislikes
  inCookbookCount
  isEditorChoice
  isGold1000
  videoFileId
  isSpecialProject
  preparationTime
  aggregateRating {
    ratingValue
    __typename
  }
  recipeCover {
    imageUrl
    imageLink {
      ...ImageLink
      __typename
    }
    __typename
  }
  createUser {
    id
    fullName
    __typename
  }
  composition {
    ingredient {
      id
      name
      relativeUrl
      __typename
    }
    __typename
  }
  videoFile {
    duration
    __typename
  }
  navigationTags {
    id
    name
    slug
    __typename
  }
  personalProps {
    cookMenuIds
    isInCookbook
    __typename
  }
  recipeSteps {
    id
    description
    __typename
  }
  __typename
}

fragment ImageLink on ImageLinkModel {
  url
  folder
  kind
  __typename
}
"""
